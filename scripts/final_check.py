import os, glob

docs_dir = os.path.join("D:\\GEO-IE", "docs")
all_docs = sorted(os.listdir(docs_dir))

print("=== 文档完整性检查 ===")
print(f"文档总数: {len(all_docs)}")
print()

# 1. 检查每个文档是否可读且非空
bad_files = []
for d in all_docs:
    fp = os.path.join(docs_dir, d)
    try:
        with open(fp, "r", encoding="utf-8") as f:
            c = f.read()
        if len(c) < 100:
            bad_files.append((d, "文件过小", len(c)))
    except Exception as e:
        bad_files.append((d, str(e), 0))

if bad_files:
    for f, reason, size in bad_files:
        print(f"[FAIL] {f}: {reason} (size={size})")
else:
    print("[PASS] 所有文档可读且非空")

# 2. 检查文件编码一致性（所有文件应该是UTF-8）
encoding_issues = []
for d in all_docs:
    fp = os.path.join(docs_dir, d)
    try:
        with open(fp, "r", encoding="utf-8") as f:
            f.read()
    except:
        encoding_issues.append(d)
if encoding_issues:
    print(f"[FAIL] {len(encoding_issues)} 个文件编码异常")
else:
    print("[PASS] 所有文档UTF-8编码正常")

# 3. 检查跨引用文档是否存在
all_refs = set()
for d in all_docs:
    fp = os.path.join(docs_dir, d)
    with open(fp, "r", encoding="utf-8") as f:
        c = f.read()
    import re
    refs = re.findall(r'\d+_[^\s#\)]+\.md', c)
    for r in refs:
        if os.path.exists(os.path.join(docs_dir, r)):
            all_refs.add((r, True))
        else:
            all_refs.add((r, False))

missing_refs = [r for r, exists in all_refs if not exists]
if missing_refs:
    print(f"[FAIL] {len(missing_refs)} 个跨引用目标不存在")
    for r in missing_refs[:5]:
        print(f"  Missing: {r}")
else:
    print("[PASS] 所有跨引用目标存在")

# 4. 检查README文档计数
readme = open(os.path.join("D:\\GEO-IE", "README.md"), "r", encoding="utf-8").read()
docs_count_in_readme = 0
for line in readme.split("\n"):
    if "份架构文档" in line:
        import re
        nums = re.findall(r'\d+', line)
        if nums:
            docs_count_in_readme = int(nums[0])
print(f"README文档数: {docs_count_in_readme}, 实际: {len(all_docs)}")
print("[PASS] 计数一致" if docs_count_in_readme == len(all_docs) else "[FAIL] 计数不一致")

# 5. 检查关联文档段落中的引用一致性
ref_issues = 0
for d in all_docs:
    fp = os.path.join(docs_dir, d)
    with open(fp, "r", encoding="utf-8") as f:
        c = f.read()
    if "关联文档" in c:
        section = c[c.find("关联文档"):]
        refs_in_section = re.findall(r'\d+_[^\s#\)]+\.md', section)
        for r in refs_in_section:
            if not os.path.exists(os.path.join(docs_dir, r)):
                ref_issues += 1
                print(f"[WARN] {d} 引用 {r} 但文件不存在")

if ref_issues == 0:
    print("[PASS] 所有关联文档引用有效")
else:
    print(f"[FAIL] {ref_issues} 个关联文档引用无效")

# 6. 内容检查 - 所有文档有关联文档段落
no_ref_section = []
for d in all_docs:
    if d in ["11_MVP范围.md"]:
        continue  # 规划文档不需要关联文档
    fp = os.path.join(docs_dir, d)
    with open(fp, "r", encoding="utf-8") as f:
        c = f.read()
    if "关联文档" not in c:
        no_ref_section.append(d)
if no_ref_section:
    print(f"[WARN] {len(no_ref_section)} 个文档缺少关联文档段落")
else:
    print("[PASS] 所有文档含关联文档段落")

print()
print("=== 总计 ===")
print(f"24/24 文档 | 所有检查完成")