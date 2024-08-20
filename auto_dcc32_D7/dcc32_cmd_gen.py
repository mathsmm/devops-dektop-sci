################################################################################
### GERADOR DE COMANDOS PARA O DCC32                                         ###
################################################################################

import subprocess, os, errno
from pathlib import Path
from dir_utils.dir_utils import all_files_to_dict


# Dicionário de caminhos de projetos. O primeiro caminho é onde o ".dpr" está.
# Os outros caminhos são inclusões de fontes compartilhados
PROJECT_DIRS_DICT = {
    "vpra": ["c:\\dw\\practice", "c:\\dw\\sci", "c:\\dwsci"]
}

# Dicionário que mapeia extensões de arquivos para flags passadas ao DCC32
FLAG_FILE_EXT_DICT = {
    ".dcu": "U",
    ".res": "R",
    ".obj": "O",
    ".pas": "I",
    ".dfm": "I",
    ".inc": "I"
}

# Caminho para onde vão os arquivos gerados por este programa
OUT_DIR = "out"

# Argumento do programa. Qual projeto
ext_var_1 = "vpra"

# Argumento do programa. Caminho do Delphi
ext_var_2 = "C:\\Program Files (x86)\\Borland\\Delphi7"

# Caminho do DCC32
delphi_path = Path(ext_var_2)

# Armazena todos os diretórios mais externos que o projeto usa
project_paths: 'list[Path]' = []
for dir in PROJECT_DIRS_DICT[ext_var_1]:
    project_paths.append(Path(dir))

# Armazena uma lista de dicionários. Cada dicionário tem todos os arquivos
# de um 'project_path'
file_dict_list: 'list[dict]' = []

# Lista que contém nomes que não são incluídos nos dicionários de arquivos
file_exclusions = ['.svn','.db','.jpg','.~']

# Armazena caminhos para informar nas flags passadas ao DCC32
flag_paths = {"U": [], "R": [], "O": [], "I": []}

def flag_paths_to_cmd() -> str:
    """Itera sobre o dicionário 'flag_paths' e monta um comando para ser passado
    ao DCC32. Este comando já vem com um espaço no começo e entre as flags
    """
    result_cmd = ""
    for flag in flag_paths.keys():
        # Se não houver caminhos para incluir na flag, pula ela
        if len(flag_paths[flag]) == 0:
            continue

        result_cmd += " -" + flag
        for path in flag_paths[flag]:
            result_cmd += '"' + path + '";'

        # Tira o último caractere que é um ponto-e-vírgula
        result_cmd = result_cmd[:-1]

    return result_cmd

def append_file_path_to_flag_paths(file: str):
    file_ext = file[file.index('.'):]
    if file_ext not in FLAG_FILE_EXT_DICT.keys():
        raise Exception(f"A EXTENSÃO '{file_ext}' NÃO EXISTE NO FLAG_FILE_EXT_DICT")

    for d in file_dict_list:
        file_path = d.get(file, None)
        if file_path is not None:
            flag_paths[FLAG_FILE_EXT_DICT[file_ext]].append(file_path)
            return

    raise Exception(f"NÃO FOI ENCONTRADO NOS DICIONÁRIOS")

def main():
    try:
        lib_path_file = open("library_path.txt", "rt")
    except Exception as e:
        try:
            lib_path_file = open("auto_dcc32_D7\\library_path.txt", "rt")
        except Exception as e:
            raise Exception("ERRO AO ABRIR O ARQUIVO 'library_path.txt':", str(e))
    lib_path = lib_path_file.read().replace('$(DELPHI)', str(delphi_path))
    lib_path_file.close()

    try:
        os.makedirs(OUT_DIR)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise Exception(f"ERRO AO CRIAR PASTA {OUT_DIR}")

    try:
        os.remove(f"{OUT_DIR}\\auto_dcc32.cmds")
    except OSError as e:
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise Exception("ERRO AO EXCLUIR ARQUIVO 'auto_dcc32.cmds'")

    for path in lib_path.rsplit(";"):
        flag_paths["U"].append(path)

    i = 0
    for path in project_paths:
        print(f'CONSULTANDO ARQUIVOS DO CAMINHO "{str(path)}"')
        file_dict_list.append(all_files_to_dict(str(path), file_exclusions))
        f = open(OUT_DIR+"\\dict_"+str(path).replace('\\','_').replace(':','')+".txt", "wt")
        for file, path in file_dict_list[i].items():
            f.write(path + '\\' + file + "\n")
        f.close()
        i += 1

    print("INICIANDO CONSTRUÇÃO DO COMANDO DCC32")
    last_cmd = ""
    cmd = ""
    halt = False
    i = 0
    while True:
        i += 1
        last_cmd = cmd
        cmd = f'DCC32 -M{flag_paths_to_cmd()} {PROJECT_DIRS_DICT[ext_var_1][0]}\\practice.dpr'
        proc_dcc32 = subprocess.Popen(args=cmd, shell=True, stdout=subprocess.PIPE)
        out, err = proc_dcc32.communicate()

        out_decoded = out.decode("utf-8")
        if 'Fatal: File not found: ' in out_decoded:
            file = out_decoded[out_decoded.index("Fatal: File not found: ")+24:-1]
            file = file[:file.index("'")]
            file = file.lower()
            try:
                append_file_path_to_flag_paths(file)
            except Exception as e:
                print(f"COMANDO {i}: ERRO AO INCLUIR ARQUIVO '{file}': {str(e)}")
                halt = True
        # elif 'was compiled with a different version of' in out_decoded:
        #     # https://stackoverflow.com/questions/429275/why-are-my-units-compiled-with-a-different-version-of-my-own-files
        #     # Consultar resposta do usuário Toon Krijthe para entender o problema
        #     # Aqui, o compilador pode informar uma unit ou uma rotina. Se informar unit, esta
        #     # unit deve ser incluída
        #     pass
        else:
            print(f"COMANDO {i}: ERRO NÃO TRATADO DO DCC32: {out_decoded}")
            halt = True

        try:
            cmd_file = open(f"{OUT_DIR}\\auto_dcc32.cmds", "wt")
        except Exception as e:
            print(f"COMANDO {i}: ERRO AO ABRIR O ARQUIVO 'practice.cmd' PARA SALVÁ-LO: {str(e)}\n")
            print(f"ÚLTIMO COMANDO: \n{cmd}")
            break

        cmd_file.write(f"ULTIMO: {last_cmd}\n")
        cmd_file.write(f"ATUAL: {cmd}\n")
        cmd_file.close()
        if halt: break
        print(f"COMANDO {i}: BEM SUCEDIDO. ADICIONADO '{file}'")

if __name__=="__main__":
    main()