from rdkit import Chem
import numpy as np
import os
import glob
import warnings
warnings.filterwarnings('ignore', 'Warning - no explicit hydrogens in mol2 file but needed for formal charge estimation.')
import csv

def Mol2MolSupplier(file=None, sanitize=False):
    mols = []
    with open(file, 'r') as f:
        doc = [line for line in f.readlines()]

    start = [index for (index, p) in enumerate(doc) if '@<TRIPOS>MOLECULE' in p]
    start.append(len(doc) + 1)

    interval = list(zip(start[:-1], start[1:]))
    for i in interval:
        block = ",".join(doc[i[0]:i[1]]).replace(',', '')
        m = Chem.MolFromMol2Block(block, sanitize=sanitize)
        mols.append(m)
    return mols
   

def calculate_distances(ref_mol_file, mol_file):
    """
    计算分子集合中所有分子与参考分子之间的距离

    参数:
        - ref_mol_file: str, 参考分子文件路径
        - mol_file: str, 待处理分子文件路径

    返回值:
        - distances: list, 所有分子与参考分子之间的距离，单位为埃
    """
    # 读取参考分子
    #ref_mol = Chem.MolFromMol2File(ref_mol_file, sanitize=False)
    ref_mol = Chem.MolFromMol2File(ref_mol_file, sanitize=False, removeHs=False, cleanupSubstructures=True)

    # 读取待处理分子
    mols = Mol2MolSupplier(mol_file)

    # 将参考分子添加到待处理分子集合中
    mols.append(ref_mol)

    # 对每个分子计算中心坐标

    #center_coord = []
    #for mol in mols:
        #coord = []
        #for i, atom in enumerate(mol.GetAtoms()):
            #coord.append([mol.GetConformer().GetAtomPosition(i).x,
                         #mol.GetConformer().GetAtomPosition(i).y,
                          #mol.GetConformer().GetAtomPosition(i).z])
        #center_coord.append(np.average(coord, 0))
    
    center_coord = []
    for mol in mols:
        if mol is None:
            # 如果分子对象为空，跳过当前循环
            continue
        coord = []
        for i, atom in enumerate(mol.GetAtoms()):
            coord.append([mol.GetConformer().GetAtomPosition(i).x,
                          mol.GetConformer().GetAtomPosition(i).y,
                          mol.GetConformer().GetAtomPosition(i).z])
        center_coord.append(np.average(coord, 0))


    # 对参考分子和待处理分子计算距离
    ref_center = center_coord[-1]
    distances = []
    for i in center_coord[:-1]:
        distances.append(np.sqrt(np.sum((ref_center - i) ** 2)))
    return distances


# 指定文件夹路径
folder_path_ligand = 'C:/Users/lenovo/origin/'
folder_path_dock = 'C:/Users/lenovo/output_origin_pdbbind_site_specific.tar/output_origin_pdbbind_site_specific'
#可替换其他文件夹

# 获取所有子文件夹
subfolders_ligand = [f.path for f in os.scandir(folder_path_ligand) if f.is_dir()]
subfolders_dock = [f.path for f in os.scandir(folder_path_dock) if f.is_dir()]

# 遍历所有子文件夹，获取每个子文件夹中所有 mol2 文件的路径
mol2_files_ligand = []
mol2_files_dock = []



for folder in subfolders_ligand:
    mol2_files_ligand.extend(glob.glob(os.path.join(folder, '*.mol2')))

for folder in subfolders_dock:
    mol2_files_dock.extend(glob.glob(os.path.join(folder, '*.mol2')))

    
#删除不合适配体（暂时无用）
'''
ligand_set = {'/mnt/c/Users/86173/rmsd/origin/origin/1epq/1epq_ligand.mol2', '/path/to/file2', '/path/to/file3', '/path/to/file4'}
dock_set = {'/mnt/c/Users/86173/rmsd/output_origin_pdbbind_site_specific.tar/output_origin_pdbbind_site_specific/1epq/1epq_ligand.mol2', '/path/to/file2', '/path/to/file3', '/path/to/file4'}


for path in ligand_set:
    if path in mol2_files_ligand:
        mol2_files_ligand.remove(path)
for patha in dock_set:
    if patha in mol2_files_dock:
        mol2_files_dock.remove(patha)
'''

docks = mol2_files_dock
ligands = mol2_files_ligand

results = [] 

#with open('results_a.txt', 'w') as f:
 #   for ligand_l, dock_l in zip(ligands, docks):
  #      try:
   #         dist = calculate_distances(ligand_l, dock_l)
    #        results.append(dist)
     #       #print(results)
      #      f.write(f'{np.array(dist)}\n')
       # except AttributeError:
        #    continue

with open('results_spec.csv', 'w', newline='') as f:
    writer = csv.writer(f, delimiter=',')
    for ligand_l, dock_l in zip(ligands, docks):
        try:
            dist = calculate_distances(ligand_l, dock_l)
            results.append(dist)
            # 将 dist 写入 CSV 文件，以逗号分隔
            writer.writerow(dist)
        except AttributeError:
            continue