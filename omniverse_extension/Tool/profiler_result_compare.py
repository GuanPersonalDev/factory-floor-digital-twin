import pstats

# 載入兩個 profile
without_ext = pstats.Stats("cProfile_2026-05-16T11-22-40.prof")
with_ext = pstats.Stats("cProfile_2026-05-16T11-23-35.prof")

# 分別建立 function -> cumtime 的 dict
def build_cumtime_dict(stats):
    result = {}
    for func, (cc, nc, tt, ct, callers) in stats.stats.items():
        filename, lineno, funcname = func
        key = f"{filename.split('/')[-1]}:{lineno}({funcname})"
        result[key] = ct
    return result

without = build_cumtime_dict(without_ext)
with_e = build_cumtime_dict(with_ext)

# 計算差異，只顯示 with_ext 比 without_ext 多出來的部分
diff = []
for key in with_e:
    t_with = with_e[key]
    t_without = without.get(key, 0)
    delta = t_with - t_without
    if delta > 0.001:  # 只顯示差距超過 1ms 的
        diff.append((delta, key))

diff.sort(reverse=True)
for delta, key in diff[:20]:
    print(f"{delta*1000:8.2f} ms  {key}")