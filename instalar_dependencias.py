"""
Script para instalar dependências com diferentes métodos para resolver problemas de conexão.
"""

import subprocess
import sys
import os

def instalar_com_metodo_1():
    """Método 1: Instalação com hosts confiáveis"""
    print("=== MÉTODO 1: Instalação com hosts confiáveis ===")
    try:
        comando = [
            sys.executable, "-m", "pip", "install",
            "--trusted-host", "pypi.org",
            "--trusted-host", "pypi.python.org", 
            "--trusted-host", "files.pythonhosted.org",
            "PyPDF2"
        ]
        subprocess.check_call(comando)
        print("✅ PyPDF2 instalado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def instalar_com_metodo_2():
    """Método 2: Instalação com timeout aumentado"""
    print("=== MÉTODO 2: Instalação com timeout aumentado ===")
    try:
        comando = [
            sys.executable, "-m", "pip", "install",
            "--timeout", "300",  # 5 minutos de timeout
            "PyPDF2"
        ]
        subprocess.check_call(comando)
        print("✅ PyPDF2 instalado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def instalar_com_metodo_3():
    """Método 3: Instalação usando mirror alternativo"""
    print("=== MÉTODO 3: Instalação usando mirror alternativo ===")
    try:
        comando = [
            sys.executable, "-m", "pip", "install",
            "-i", "https://pypi.tuna.tsinghua.edu.cn/simple/",
            "PyPDF2"
        ]
        subprocess.check_call(comando)
        print("✅ PyPDF2 instalado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def instalar_com_metodo_4():
    """Método 4: Instalação offline (se você tiver o arquivo .whl)"""
    print("=== MÉTODO 4: Instalação offline ===")
    print("Para este método, você precisa:")
    print("1. Baixar o arquivo .whl do PyPDF2 de: https://pypi.org/project/PyPDF2/#files")
    print("2. Colocar o arquivo na mesma pasta deste script")
    print("3. Executar: pip install nome_do_arquivo.whl")
    return False

def verificar_instalacao():
    """Verifica se PyPDF2 está instalado"""
    try:
        import PyPDF2
        print("✅ PyPDF2 já está instalado!")
        return True
    except ImportError:
        print("❌ PyPDF2 não está instalado")
        return False

def main():
    print("=== INSTALADOR DE DEPENDÊNCIAS - ANALISADOR DOCUMENTAL ===\n")
    
    # Verifica se já está instalado
    if verificar_instalacao():
        return
    
    print("Tentando instalar PyPDF2...\n")
    
    # Tenta diferentes métodos
    metodos = [
        instalar_com_metodo_1,
        instalar_com_metodo_2,
        instalar_com_metodo_3
    ]
    
    for i, metodo in enumerate(metodos, 1):
        print(f"\n--- Tentativa {i} ---")
        if metodo():
            break
        print("Tentando próximo método...\n")
    else:
        print("\n❌ Todos os métodos online falharam.")
        instalar_com_metodo_4()
    
    # Verifica novamente
    if verificar_instalacao():
        print("\n🎉 Instalação concluída com sucesso!")
    else:
        print("\n⚠️  A classe funcionará com funcionalidades limitadas.")

if __name__ == "__main__":
    main()