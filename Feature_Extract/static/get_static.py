import os
import shutil
import sys
import logging
import subprocess

from classify_files import classify_c_files

logging.basicConfig(format = '%(asctime)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
def log(mess):
     logging.info(mess)

def run_java_slice(project_path):
    """
    Chạy Java để tách hàm trong file .c bằng Eclipse CDT parser
    """

    path = os.path.dirname(os.path.realpath(__file__))
    java_classpath = (
        f"{path}/cut/out/production/cut:"
        f"{path}/cut/lib/cdt.core-5.6.0.201402142303.jar:"
        f"{path}/cut/lib/equinox.common-3.6.200.v20130402-1505.jar"
    )
    command = [
        "java",
        "-classpath",
        java_classpath,
        "slice.Main",
        project_path
    ]

    print("Running Java AST slicer...")
    try:
        subprocess.run(command, check=True)
        print("Finished slicing functions.")
    except subprocess.CalledProcessError as e:
        print("Error running Java slicer:", e)

def run_seven_edges(project_path, logDir, log=print):
    log("Start to get seven edges...")
    path = os.path.dirname(os.path.realpath(__file__))

    # Vị trí thư mục sevenEdges
    seven_edges_dir = os.path.join(path, "side/src/sevenEdges/")
    os.chdir(seven_edges_dir)

    # Build classpath cho Java
    classpath = ":".join([
        os.path.join(path, "side/out/production/side"),
        os.path.join(path, "side/lib/cdt.core-5.6.0.201402142303.jar"),
        os.path.join(path, "side/lib/equinox.common-3.6.200.v20130402-1505.jar")
    ])

    # Lệnh 1: run sevenEdges.Main
    log_path_1 = os.path.join(logDir, "1sevenEdges.Main.log")
    cmd1 = ["java", "-classpath", classpath, "sevenEdges.Main", project_path]
    with open(log_path_1, "w") as log_file:
        try:
            subprocess.run(cmd1, stdout=log_file, stderr=subprocess.STDOUT, check=True)
            log(f"Finished sevenEdges.Main (log: {log_path_1})")
        except subprocess.CalledProcessError:
            log(f"[Error] Failed to run sevenEdges.Main. See log: {log_path_1}")

    # Lệnh 2: run sevenEdges.concateJoern
    log_path_2 = os.path.join(logDir, "2sevenEdges.concateJoern.log")
    cmd2 = ["java", "-classpath", classpath, "sevenEdges.concateJoern", project_path]
    with open(log_path_2, "w") as log_file:
        try:
            subprocess.run(cmd2, stdout=log_file, stderr=subprocess.STDOUT, check=True)
            log(f"Finished sevenEdges.concateJoern (log: {log_path_2})")
        except subprocess.CalledProcessError:
            log(f"[Error] Failed to run sevenEdges.concateJoern. See log: {log_path_2}")

def run_static_feature_extraction(project_path, logDir, log=print):
    path = os.path.dirname(os.path.realpath(__file__))

    # Xóa thư mục cũ nếu tồn tại
    cfg = os.path.join(project_path, "cfg")
    cfg_result = os.path.join(project_path, "cfg_result")
    cfg_result_exception = os.path.join(project_path, "cfg_result_exception")
    static_dir = os.path.join(project_path, "static")
    cut_dir = os.path.join(project_path, "cut/good")
    joern_dir = os.path.join(path, "joern-cli_new")

    for dir_to_remove in [cfg, cfg_result, cfg_result_exception]:
        if os.path.exists(dir_to_remove):
            shutil.rmtree(dir_to_remove)
    
    log("Start to get cfg path by Joern and concatenate...")

    # Tạo lại thư mục cfg
    os.makedirs(cfg, exist_ok=True)

    # --- Step 1: getcfg.py ---
    os.chdir(joern_dir)
    try:
        subprocess.run(["python3", "getcfg.py", cut_dir, cfg], check=True)
        log("getcfg.py executed successfully")
    except subprocess.CalledProcessError as e:
        log(f"[Error] getcfg.py failed: {e}")

    # --- Step 2: run cfg2path.GetCfgInfo ---
    cfg2path_src = os.path.join(path, "cfg2path/src")
    classpath_cfg2path = os.path.join(path, "cfg2path/out/production/cfg2path")
    log_file_3 = os.path.join(logDir, "3cfg2path.GetCfgInfo.log")

    os.chdir(cfg2path_src)
    try:
        with open(log_file_3, "w") as logf:
            subprocess.run([
                "java", "-classpath", classpath_cfg2path,
                "cfg2path.GetCfgInfo", cfg, cfg_result
            ], stdout=logf, stderr=subprocess.STDOUT, check=True)
        log("cfg2path.GetCfgInfo executed successfully")
    except subprocess.CalledProcessError:
        log(f"[Error] Failed to run cfg2path.GetCfgInfo. See log: {log_file_3}")

    # --- Step 3: check_cfg.py ---
    os.chdir(path)
    try:
        subprocess.run([
            "python3", os.path.join(path, "check_cfg.py"),
            cfg_result, cfg_result_exception
        ], check=True)
        log("check_cfg.py executed successfully")
    except subprocess.CalledProcessError as e:
        log(f"[Error] check_cfg.py failed: {e}")

    # --- Step 4: run cfg2path.Concate2File ---
    log_file_4 = os.path.join(logDir, "4cfg2path.Concate2File.log")
    os.chdir(cfg2path_src)
    try:
        with open(log_file_4, "w") as logf:
            subprocess.run([
                "java", "-classpath", classpath_cfg2path,
                "cfg2path.Concate2File", cfg_result, static_dir
            ], stdout=logf, stderr=subprocess.STDOUT, check=True)
        log("cfg2path.Concate2File executed successfully")
    except subprocess.CalledProcessError:
        log(f"[Error] Failed to run cfg2path.Concate2File. See log: {log_file_4}")

    log("============================================================================================================")
    log(f"Extracted static feature stored in : {static_dir}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_static.py <project_path>")
        sys.exit(1)

    # Get the project path from command line arguments
    path = os.path.dirname(os.path.realpath(__file__))
    project_path =sys.argv[1]
    output_path = os.path.join(path, "output")

    log(f'project : {project_path}')
    if not os.path.exists(project_path):
        log(f"project {project_path} not exist!")
        sys.exit(1)

    logDir = path+"/log"
    if not os.path.exists(logDir):
        os.mkdir(logDir)

    # if os.path.exists(path+"/cut"):
    #     shutil.rmtree(path+"/cut")
    # if os.path.exists(path+"/out"):
    #     shutil.rmtree(path+"/out")
    # if os.path.exists(path+"/static"):
    #     shutil.rmtree(path+"/static")

    log("start to get function segmentation... ")
    
    # Classify files in the project directory
    print("[+] Source path:", project_path)
    print("[+] Store path:", output_path)
    classify_c_files(project_path, output_path)

    # Slice the functions in the classified files
    run_java_slice(output_path)

    log("start to get graphRelation by joern... ")
    os.chdir(path + "/joern-cli")

    if os.path.exists("parse_result"):
        shutil.rmtree("parse_result")
    if os.path.exists("raw_result"):
        shutil.rmtree("raw_result")
    if os.path.exists("result"):
        shutil.rmtree("result")
    os.mkdir("parse_result")
    os.mkdir("raw_result")
    os.mkdir("result")
    os.system("python3 main.py "+ output_path +" 2>main.py.log")

    run_seven_edges(output_path, logDir)

    run_static_feature_extraction(output_path, logDir)

    sys.exit(0)

    log("start to get seven edges...")
    os.chdir(path+"/side/src/sevenEdges/")
    os.system("java -classpath "+path+"/side/out/production/side:"+path+"/static_do/side/lib/cdt.core-5.6.0.201402142303.jar:"+path+"/static_do/side/lib/equinox.common-3.6.200.v20130402-1505.jar sevenEdges.Main "+path+" >"+logDir+"/1sevenEdges.Main.log")
    os.system("java -classpath "+path+"/side/out/production/side:"+path+"/static_do/side/lib/cdt.core-5.6.0.201402142303.jar:"+path+"/static_do/side/lib/equinox.common-3.6.200.v20130402-1505.jar sevenEdges.concateJoern "+path+" >"+logDir+"/2sevenEdges.concateJoern.log")



    if os.path.exists(path+"/cfg"):
        shutil.rmtree(path+"/cfg")
    if os.path.exists(path+"/cfg_result"):
        shutil.rmtree(path+"/cfg_result")

    log("start to get cfgpath  by joern and concate... ")
    current_dir=path
    os.chdir(current_dir+"/joern-cli_new")
    sliceDir=current_dir+"/cut/good"
    cfg=current_dir+"/cfg"
    cfg_result=current_dir+"/cfg_result"
    sevenEdges=current_dir+"/static"
    if os.path.exists(cfg):
        shutil.rmtree(cfg)
    os.mkdir(cfg)
    os.system("python3 getcfg.py "+sliceDir+" "+cfg)
    os.chdir(current_dir+"/static_do/cfg2path/src")
    os.system("java -classpath "+current_dir+"/static_do/cfg2path/out/production/cfg2path "+"cfg2path.GetCfgInfo "+cfg+" "+cfg_result+" >"+logDir+"/3cfg2path.GetCfgInfo.log")

    os.chdir(current_dir)
    os.system("python3 "+current_dir+"/check_cfg.py "+current_dir+"/cfg_result "+current_dir+"/cfg_result_exception")

    os.chdir(current_dir+"/static_do/cfg2path/src")
    os.system("java -classpath "+current_dir+"/static_do/cfg2path/out/production/cfg2path "+"cfg2path.Concate2File "+cfg_result+" "+sevenEdges+" >"+logDir+"/4cfg2path.Concate2File.log")

    print("============================================================================================================")
    log(f"extracted static feature stored in : {path}/static/")