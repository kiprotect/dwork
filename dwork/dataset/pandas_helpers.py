from collections import defaultdict
import numpy as np
import random


def epsilon(pr, pf):
    return max(
        np.log((pr * pf + 1 - pr) / (pr * pf)),
        np.log((pr * (1 - pf) + 1 - pr) / (pr * (1 - pf))),
    )


def epsilon_flip(pr, pf):
    a = (pr * (1 - pf) + 1 - pr) / (pr * pf)

    return max(np.log(a), np.log(1 / a))


def randomize(fds, pr, pf, flip=False):
    fdsr = fds.copy()
    for i in range(len(fds)):
        for j in range(len(fds[i])):
            if random.random() < pr:
                if flip:
                    if random.random() < pf:
                        fdsr[i, j] = not fdsr[i, j]
                else:
                    if random.random() < pf:
                        fdsr[i, j] = True
                    else:
                        fdsr[i, j] = False
    return fdsr


def discretize(df, exclude=None):
    mapping = defaultdict(dict)
    reverse_mapping = {}
    i = 0
    for column in df.columns:
        if exclude is not None and column in exclude:
            continue
        for value in sorted(df[column].unique()):
            mapping[column][value] = i
            reverse_mapping[i] = (column, value)
            i += 1
    fds = np.zeros((len(df), i), dtype=np.uint8)
    for i, (_, entry) in enumerate(df.iterrows()):
        for column, value_map in mapping.items():
            fds[i, value_map[entry[column]]] = 1
    return fds, mapping, reverse_mapping


def reconstruct(fds, mapping, reverse_mapping, pr, pf):
    records = []
    ps = {}
    n = len(fds)
    for i in range(fds.shape[1]):
        # we calculate the base probability of this feature
        s1r = np.sum(fds[:, i] == True)
        ps[i] = min(max(0, (s1r - pr * pf * n) / ((1 - pr) * n)), 1)
    for i, row in enumerate(fds):
        record = {}
        for key, values in mapping.items():
            possible_values = []
            p_tot = 0.0
            for value, column in values.items():
                if row[column] == 1:
                    p_tot += ps[column]
                    possible_values.append((value, ps[column]))
            if not possible_values:
                possible_values = [
                    (value, ps[column]) for value, column in values.items()
                ]
                p_tot = sum([ps[column] for column in values.values()])
            rv = random.random() * p_tot
            i = 0
            p = 0.0
            while p < rv:
                p += possible_values[i][1]
                i += 1
            record[key] = possible_values[i - 1][0]
        records.append(record)
    return pd.DataFrame.from_records(records)


def count(filters, mapping, ds):
    """
    Returns the count of items matching a given set of attribute values.
    """
    dsf = ds
    for key, value in filters:
        if not isinstance(value, (list, tuple)):
            value = (value,)
        condition = None
        for v in value:
            column = mapping[key][v]
            new_condition = dsf[:, column] == True
            if condition is None:
                condition = new_condition
            else:
                condition = condition | new_condition
        dsf = dsf[np.where(condition)]
    return len(dsf)


def count_p(filters, mapping, ds, dsr, pr, pf, flip=False):
    """
    Returns the count of items matching a given set of attribute values.
    """
    c = 0
    cr = 0
    p0s = {}
    for key, value in filters:
        if not isinstance(value, (list, tuple)):
            value = (value,)
        # we need to estimate whether at least one element is True
        # so we estimate whether all elements are False given
        # the data instead and then subtract 1 from that value
        for v in value:
            column = mapping[key][v]
            s1r = np.sum(ds[:, column] == True)
            s1rr = np.sum(dsr[:, column] == True)
            p0s[column] = min(
                max(0, 1.0 - (s1r - pr * pf * len(ds)) / ((1 - pr) * len(ds))), 1
            )
    var = 0.0
    for i, row in enumerate(ds):
        pt = 1.0
        ptr = 1.0
        for key, value in filters:
            if not isinstance(value, (list, tuple)):
                value = (value,)
            # we need to estimate whether at least one element is True
            # so we estimate whether all elements are False given
            # the data instead and then subtract 1 from that value
            pev = 1.0
            pevr = 1.0
            for v in value:
                column = mapping[key][v]
                ev = row[column]
                p0 = p0s[column]
                pevr *= p0
                # here we should take into account the variance of the estimate of
                # p0, which is the only unknown parameter in this scheme
                if ev == False:
                    # pev *= pr*(1-pf)+1-pr
                    # Flipping
                    if flip:
                        pev *= (1 - pr) * p0 / (pr * (1 - p0) + (1 - pr) * p0)
                    else:
                        pev *= (
                            (pr * (1 - pf) + (1 - pr))
                            * p0
                            / (pr * (1 - pf) + (1 - pr) * p0)
                        )
                    # probability: pr*pf+(1-pr)
                else:
                    # pev *= pr*pf
                    # Flipping
                    if flip:
                        pev *= pr * p0 / (pr * p0 + (1 - pr) * (1 - p0))
                    else:
                        pev *= pr * pf * p0 / (pr * pf + (1 - pr) * (1 - p0))
                    # probability: pr*(1-pf)
            pt *= 1.0 - pev
            ptr *= 1.0 - pevr
        c += pt
        cr += ptr
        var += pt * (1 - pt)
    return c, cr, np.sqrt(var)


def sample_p(mapping, reverse_mapping, ds, pr, pf, flip=False, limit=10, verbose=False):
    """
    Generates random samples from the dataset based on a hierarchical sampling method.
    
    - Given the selected features, calculate the probabilities for all other features
    - Randomly select one feature based on its probability
    - Repeat until the frequency becomes too small
    
    We keep a list of features that we have already explored at the current position
    in the feature history, so we can avoid going back to them. When we go down the
    feature tree, we push this list together with the current "pt" vector to a history
    structure. If we then go back up, we restore them.
    """
    explored = set()
    history = []
    features = {}
    # here we store the probabilities
    pt = np.ones((ds.shape[0],))
    while True:
        # we calculate the probabilities for all features in the current state
        p0s = {}
        for key, values in mapping.items():
            if key in features:
                # we skip features for attributes that we have already set
                continue
            for value, column in values.items():
                if column in explored:
                    continue
                s1r = np.sum((ds[:, column] == True) * pt)
                p0s[column] = min(
                    max(0, 1.0 - (s1r - pr * pf * len(ds)) / ((1 - pr) * len(ds))), 1
                )
            p0s_sum = sum([p[1] for p in p0s.items()])
            if not p0s or p0s_sum == 0:
                continue
            break
        else:
            if verbose:
                print(features, np.sum(pt))
            yield (np.sum(pt), features)
            # we have no possible candidates left here, we need to go up
            if not history:
                break
            pt, explored, features = history.pop()
            continue

        p0s_items = []
        p = 0
        for i, p0 in enumerate(p0s.items()):
            p += p0[1] / p0s_sum
            p0s_items.append((p0[0], p))

        p0s_items = sorted(p0s_items, key=lambda x: x[1])

        # we select the column that is most probably
        column = p0s_items[0][0]
        # we add this column to the list of explored columns at this hierarchy level
        explored.add(column)

        key, value = reverse_mapping[column]

        # we calculate the base probability of this feature
        s1r = np.sum((ds[:, column] == True) * pt)

        p0 = min(max(0, 1.0 - (s1r - pr * pf * len(ds)) / ((1 - pr) * len(ds))), 1)

        # here we should take into account the variance of the estimate of
        # p0, which is the only unknown parameter in this scheme
        if flip:
            pev_false = (1 - pr) * p0 / (pr * (1 - p0) + (1 - pr) * p0)
            pev_true = pr * p0 / (pr * p0 + (1 - pr) * (1 - p0))
        else:
            pev_false = (
                (pr * (1 - pf) + (1 - pr)) * p0 / (pr * (1 - pf) + (1 - pr) * p0)
            )
            if p0 == 1:
                pev_true = 0.0
            else:
                pev_true = pr * pf * p0 / (pr * pf + (1 - pr) * (1 - p0))
        # we multiple the probability vector
        new_pt = pt * (
            (ds[:, column] == 1) * (1.0 - pev_true)
            + (ds[:, column] == 0) * (1.0 - pev_false)
        )
        if sum(new_pt) < limit:
            # the probability is too small, we skip this sample
            continue
        history.append((pt, explored, features))
        pt = new_pt
        explored = explored.copy()
        features = features.copy()
        features[key] = value


def sample_p_breadth_first(
    mapping,
    reverse_mapping,
    ds,
    dsr,
    pr,
    pf,
    flip=False,
    limit=10,
    forced_attributes=None,
    min_depth=1,
    max_depth=None,
    verbose=False,
    skip_expected=False,
    interleave=None,
):
    """
    Generates random samples from the dataset based on a hierarchical sampling method.
    
    - Given the selected features, calculate the probabilities for all other features
    - Randomly select one feature based on its probability
    - Repeat until the frequency becomes too small
    
    We keep a list of features that we have already explored at the current position
    in the feature history, so we can avoid going back to them. When we go down the
    feature tree, we push this list together with the current "pt" vector to a history
    structure. If we then go back up, we restore them.
    """
    explored = set()
    features = {}
    global_failed = {}
    failed = global_failed
    depth = min_depth
    # here we store the probabilities
    pt = np.ones((ds.shape[0],))
    history = []
    new_samples = 0
    features_checked = 0
    features_skipped = 0
    while True:
        # we calculate the probabilities for all features in the current state
        p0s = {}
        for key, values in mapping.items():
            if key in features:
                # we skip features for attributes that we have already set
                continue
            if (
                forced_attributes is not None
                and len(features) < len(forced_attributes)
                and key not in forced_attributes
            ):
                continue
            for value, column in values.items():
                if column in explored:
                    continue
                if column in failed and failed[column] is True:
                    features_skipped += 1
                    continue
                s1r = np.sum((ds[:, column] == True) * pt)
                p0s[column] = min(
                    max(0, 1.0 - (s1r - pr * pf * len(ds)) / ((1 - pr) * len(ds))), 1
                )
            p0s_sum = sum([p[1] for p in p0s.items()])
            if not p0s or p0s_sum == 0:
                continue
            break
        else:
            if not history:
                if new_samples == 0:
                    break
                depth += 1
                if max_depth is not None and depth > max_depth:
                    break
                new_samples = 0
                explored = set()
                features = {}
                failed = global_failed
                pt = np.ones((ds.shape[0],))
            else:
                pt, explored, features, failed = history.pop()
            continue

        features_checked += 1
        p0s_items = []
        p = 0
        for i, p0 in enumerate(p0s.items()):
            p += p0[1] / p0s_sum
            p0s_items.append((p0[0], p))

        p0s_items = sorted(p0s_items, key=lambda x: x[1])

        # we select the column that is most probably
        column = p0s_items[0][0]

        # we add this column to the list of explored columns at this hierarchy level
        explored.add(column)
        if not column in failed:
            failed[column] = {}

        key, value = reverse_mapping[column]

        if interleave is not None:
            iv = np.random.choice(
                [0, 1], size=(ds.shape[0],), p=[1.0 - interleave, interleave]
            )
            dsc = ds[:, column]
            dso = dsr[:, column]
            # we mix the randomized with the original data
            dsc = dsc * iv + dso * (1 - iv)
            pre = pr * interleave
        else:
            dsc = ds[:, column]
            pre = pr

        # we calculate the base probability of this feature
        # s1r = np.sum((ds[:,column] == True)*pt)
        s1r = np.sum((dsc == True) * 1.0)
        p0 = min(max(0, 1.0 - (s1r - pre * pf * len(ds)) / ((1 - pre) * len(ds))), 1)

        # here we should take into account the variance of the estimate of
        # p0, which is the only unknown parameter in this scheme
        if flip:
            pev_false = (1 - pre) * p0 / (pre * (1 - p0) + (1 - pre) * p0)
            pev_true = pre * p0 / (pre * p0 + (1 - pre) * (1 - p0))
        else:
            pev_false = (
                (pre * (1 - pf) + (1 - pre)) * p0 / (pre * (1 - pf) + (1 - pre) * p0)
            )
            if p0 == 1:
                pev_true = 0.0
            else:
                pev_true = pre * pf * p0 / (pre * pf + (1 - pre) * (1 - p0))
        # we multiple the probability vector
        new_pt = pt * ((dsc == 1) * (1.0 - pev_true) + (dsc == 0) * (1.0 - pev_false))
        if limit is not None and np.sum(new_pt) < limit:
            # the probability is too small, we skip this sample and go back up
            failed[column] = True
            continue
        if len(features) == depth - 1:
            # we're at the required depth so we generate a sample and go
            # back up the hierarchy...
            sample_features = features.copy()
            sample_features[key] = value
            p_exp = np.sum(pt) * (1 - p0)
            p_obs = np.sum(new_pt)
            new_samples += 1
            if verbose:
                print("Sample:", sample_features, np.sum(new_pt))
            if (
                skip_expected
                and p_exp > 0
                and np.abs(p_obs - p_exp) / p_exp < 0.05
                and depth > 1
            ):
                # we do not publish this sample
                print("(not publishing)")
                continue
            yield (np.sum(new_pt), sample_features)
        else:
            history.append((pt, explored.copy(), features.copy(), failed))
            # we're not yet at the required depth, we keep going down
            features[key] = value
            failed = failed[column]
            pt = new_pt
