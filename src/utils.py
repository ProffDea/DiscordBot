def hrf_time_diff(current, past):
    diff = current - past
    days, rem = divmod(diff.seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    if seconds < 1:
        seconds = 1
    locals_ = locals()
    magnitudes_str = ("%s %s" % (int(locals_[magnitude]), magnitude)
                      for magnitude in ("days", "hours", "minutes", "seconds") if locals_[magnitude])
    eta_str = ", ".join(magnitudes_str)
    return eta_str
