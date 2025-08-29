import os
import re
from collections import Counter
from typing import List, Dict, Tuple, Optional, Union
from pathlib import Path
import logging
from datetime import datetime
from urllib.parse import urlparse

# Importa o gerenciador de stop words
from config import StopWordsManager

# Configuração de logging para debug e monitoramento
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AnalisadorDocumental:
    """
    Classe para análise de documentos PDF e páginas web com funcionalidades de processamento de texto
    e integração com API da OpenAI.
    
    Atributos:
        fonte (str): Caminho para arquivo PDF ou URL da página web
        tipo_fonte (str): Tipo da fonte ('pdf' ou 'web')
        conteudo (str): Conteúdo extraído da fonte
        palavras_processadas (List[str]): Lista de palavras após limpeza
        api_key (str): Chave da API da OpenAI
        info_fonte (Dict): Informações gerais da fonte
        stop_words_manager (StopWordsManager): Gerenciador de stop words
        idioma_detectado (str): Idioma detectado do conteúdo
    """
    
    def __init__(self, fonte: str, api_key: Optional[str] = None, idioma: Optional[str] = None):
        """
        Inicializa o analisador de documentos.
        
        Args:
            fonte (str): Caminho para arquivo PDF ou URL da página web
            api_key (str, optional): Chave da API da OpenAI para análise com ChatGPT
            idioma (str, optional): Idioma para stop words ('portugues', 'ingles', 'espanhol')
        """
        self.fonte = fonte
        self.tipo_fonte = self._determinar_tipo_fonte(fonte)
        self.conteudo = ""
        self.palavras_processadas = []
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.info_fonte = {}
        
        # Inicializa gerenciador de stop words
        self.stop_words_manager = StopWordsManager()
        self.idioma_detectado = idioma
        
        # Validação inicial
        self._validar_fonte()
        self._extrair_informacoes_fonte()
        self._extrair_conteudo()
        self._processar_palavras()
    
    def _determinar_tipo_fonte(self, fonte: str) -> str:
        """
        Determina se a fonte é um arquivo PDF ou uma URL web.
        
        Args:
            fonte (str): Caminho do arquivo ou URL
            
        Returns:
            str: 'pdf' ou 'web'
        """
        # Verifica se é uma URL
        try:
            resultado = urlparse(fonte)
            if resultado.scheme and resultado.netloc:
                return 'web'
        except:
            pass
        
        # Verifica se é um arquivo PDF
        if fonte.lower().endswith('.pdf'):
            return 'pdf'
        
        # Verifica se é um caminho de arquivo existente
        if os.path.exists(fonte):
            return 'pdf'
        
        # Se não conseguir determinar, assume que é web
        return 'web'
    
    def _normalizar_caminho(self, caminho: str) -> str:
        """
        Normaliza o caminho do arquivo para evitar problemas de encoding no Windows.
        
        Args:
            caminho (str): Caminho original do arquivo
            
        Returns:
            str: Caminho normalizado
        """
        try:
            # Usa pathlib para normalizar o caminho de forma segura
            path_obj = Path(caminho)
            return str(path_obj.resolve())
        except Exception as e:
            logger.warning(f"Erro ao normalizar caminho: {e}. Usando caminho original.")
            return caminho
    
    def _validar_fonte(self) -> None:
        """
        Valida se a fonte existe e é válida.
        
        Raises:
            FileNotFoundError: Se o arquivo não existir
            ValueError: Se a fonte não for válida
        """
        try:
            if self.tipo_fonte == 'pdf':
                if not os.path.exists(self.fonte):
                    raise FileNotFoundError(f"Arquivo não encontrado: {self.fonte}")
                
                if not self.fonte.lower().endswith('.pdf'):
                    raise ValueError("O arquivo deve ser um PDF")
            
            elif self.tipo_fonte == 'web':
                # Validação básica de URL
                try:
                    resultado = urlparse(self.fonte)
                    if not resultado.scheme or not resultado.netloc:
                        raise ValueError("URL inválida")
                except Exception as e:
                    raise ValueError(f"URL inválida: {e}")
            
            logger.info(f"Fonte validada: {self.fonte} (tipo: {self.tipo_fonte})")
            
        except Exception as e:
            logger.error(f"Erro na validação da fonte: {e}")
            raise
    
    def _extrair_informacoes_fonte(self) -> None:
        """
        Extrai informações gerais da fonte (PDF ou web).
        """
        try:
            if self.tipo_fonte == 'pdf':
                self._extrair_informacoes_pdf()
            elif self.tipo_fonte == 'web':
                self._extrair_informacoes_web()
            
            logger.info(f"Informações da fonte extraídas")
            
        except Exception as e:
            logger.error(f"Erro ao extrair informações da fonte: {e}")
    
    def _extrair_informacoes_pdf(self) -> None:
        """
        Extrai informações de um arquivo PDF.
        """
        # Informações básicas do arquivo (sempre disponíveis)
        self.info_fonte = {
            'tipo': 'PDF',
            'nome': os.path.basename(self.fonte),
            'caminho_completo': self.fonte,
            'tamanho_bytes': os.path.getsize(self.fonte),
            'data_modificacao': datetime.fromtimestamp(
                os.path.getmtime(self.fonte)
            ).strftime('%d/%m/%Y %H:%M:%S'),
            'total_paginas': 'Não disponível (bibliotecas não instaladas)',
            'versao_pdf': 'Não disponível',
            'criptografado': 'Não disponível',
            'metadados': {}
        }
        
        # Tenta extrair informações usando diferentes bibliotecas
        self._tentar_extrair_metadados()
    
    def _extrair_informacoes_web(self) -> None:
        """
        Extrai informações de uma página web.
        """
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # Faz requisição para obter informações básicas
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(self.fonte, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrai informações da página
            titulo = soup.find('title')
            titulo_texto = titulo.get_text().strip() if titulo else 'Sem título'
            
            # Extrai meta tags
            meta_tags = {}
            for meta in soup.find_all('meta'):
                name = meta.get('name') or meta.get('property')
                content = meta.get('content')
                if name and content:
                    meta_tags[name] = content
            
            self.info_fonte = {
                'tipo': 'Página Web',
                'url': self.fonte,
                'titulo': titulo_texto,
                'tamanho_bytes': len(response.content),
                'data_acesso': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', 'Desconhecido'),
                'encoding': response.encoding,
                'metadados': meta_tags
            }
            
        except ImportError:
            logger.warning("requests ou beautifulsoup4 não instalados. Usando informações básicas.")
            self.info_fonte = {
                'tipo': 'Página Web',
                'url': self.fonte,
                'titulo': 'Não disponível (bibliotecas não instaladas)',
                'tamanho_bytes': 0,
                'data_acesso': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'status_code': 'Não disponível',
                'content_type': 'Não disponível',
                'encoding': 'Não disponível',
                'metadados': {}
            }
        except Exception as e:
            logger.error(f"Erro ao extrair informações da web: {e}")
            self.info_fonte = {
                'tipo': 'Página Web',
                'url': self.fonte,
                'titulo': f'Erro: {str(e)}',
                'tamanho_bytes': 0,
                'data_acesso': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'status_code': 'Erro',
                'content_type': 'Erro',
                'encoding': 'Erro',
                'metadados': {}
            }
    
    def _tentar_extrair_metadados(self) -> None:
        """
        Tenta extrair metadados usando diferentes bibliotecas disponíveis.
        """
        # Tenta com PyMuPDF (fitz) primeiro
        if self._extrair_metadados_pymupdf():
            return
        
        # Tenta com pdfplumber
        if self._extrair_metadados_pdfplumber():
            return
        
        # Tenta com PyPDF2 como último recurso
        if self._extrair_metadados_pypdf2():
            return
        
        logger.info("Nenhuma biblioteca de PDF disponível para extrair metadados")
    
    def _extrair_metadados_pymupdf(self) -> bool:
        """
        Tenta extrair metadados usando PyMuPDF (fitz).
        
        Returns:
            bool: True se conseguiu extrair, False caso contrário
        """
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(self.fonte)
            
            # Informações básicas
            self.info_fonte.update({
                'total_paginas': len(doc),
                'versao_pdf': f"{doc.version}",
                'criptografado': doc.needs_pass,
            })
            
            # Metadados
            metadata = doc.metadata
            if metadata:
                self.info_fonte['metadados'] = {
                    'titulo': metadata.get('title', 'Não informado'),
                    'autor': metadata.get('author', 'Não informado'),
                    'assunto': metadata.get('subject', 'Não informado'),
                    'criador': metadata.get('creator', 'Não informado'),
                    'produtor': metadata.get('producer', 'Não informado'),
                    'data_criacao': metadata.get('creationDate', 'Não informado'),
                    'data_modificacao_meta': metadata.get('modDate', 'Não informado')
                }
            
            doc.close()
            logger.info(f"Metadados PyMuPDF extraídos: {self.info_fonte['total_paginas']} páginas")
            return True
            
        except ImportError:
            logger.info("PyMuPDF não está instalado")
            return False
        except Exception as e:
            logger.warning(f"Erro ao extrair metadados com PyMuPDF: {e}")
            return False
    
    def _extrair_metadados_pdfplumber(self) -> bool:
        """
        Tenta extrair metadados usando pdfplumber.
        
        Returns:
            bool: True se conseguiu extrair, False caso contrário
        """
        try:
            import pdfplumber
            
            with pdfplumber.open(self.fonte) as pdf:
                # Informações básicas
                self.info_fonte.update({
                    'total_paginas': len(pdf.pages),
                    'versao_pdf': 'PDF (pdfplumber)',
                    'criptografado': False,  # pdfplumber não detecta criptografia facilmente
                })
                
                # Metadados
                if hasattr(pdf, 'metadata') and pdf.metadata:
                    metadata = pdf.metadata
                    self.info_fonte['metadados'] = {
                        'titulo': metadata.get('Title', 'Não informado'),
                        'autor': metadata.get('Author', 'Não informado'),
                        'assunto': metadata.get('Subject', 'Não informado'),
                        'criador': metadata.get('Creator', 'Não informado'),
                        'produtor': metadata.get('Producer', 'Não informado'),
                        'data_criacao': metadata.get('CreationDate', 'Não informado'),
                        'data_modificacao_meta': metadata.get('ModDate', 'Não informado')
                    }
                
                logger.info(f"Metadados pdfplumber extraídos: {self.info_fonte['total_paginas']} páginas")
                return True
                
        except ImportError:
            logger.info("pdfplumber não está instalado")
            return False
        except Exception as e:
            logger.warning(f"Erro ao extrair metadados com pdfplumber: {e}")
            return False
    
    def _extrair_metadados_pypdf2(self) -> bool:
        """
        Tenta extrair metadados usando PyPDF2 (último recurso).
        
        Returns:
            bool: True se conseguiu extrair, False caso contrário
        """
        try:
            import PyPDF2
            
            with open(self.fonte, 'rb') as arquivo:
                leitor = PyPDF2.PdfReader(arquivo)
                
                # Informações básicas
                self.info_fonte.update({
                    'total_paginas': len(leitor.pages),
                    'versao_pdf': leitor.metadata.get('/PDFVersion', 'Desconhecida') if leitor.metadata else 'Desconhecida',
                    'criptografado': leitor.is_encrypted,
                })
                
                # Metadados
                if leitor.metadata:
                    metadados = leitor.metadata
                    self.info_fonte['metadados'] = {
                        'titulo': metadados.get('/Title', 'Não informado'),
                        'autor': metadados.get('/Author', 'Não informado'),
                        'assunto': metadados.get('/Subject', 'Não informado'),
                        'criador': metadados.get('/Creator', 'Não informado'),
                        'produtor': metadados.get('/Producer', 'Não informado'),
                        'data_criacao': metadados.get('/CreationDate', 'Não informado'),
                        'data_modificacao_meta': metadados.get('/ModDate', 'Não informado')
                    }
                
                logger.info(f"Metadados PyPDF2 extraídos: {self.info_fonte['total_paginas']} páginas")
                return True
                
        except ImportError:
            logger.info("PyPDF2 não está instalado")
            return False
        except Exception as e:
            logger.warning(f"Erro ao extrair metadados com PyPDF2: {e}")
            return False
    
    def _extrair_conteudo(self) -> None:
        """
        Extrai o conteúdo da fonte (PDF ou web).
        """
        try:
            if self.tipo_fonte == 'pdf':
                self._extrair_conteudo_pdf()
            elif self.tipo_fonte == 'web':
                self._extrair_conteudo_web()
            
        except Exception as e:
            logger.error(f"Erro ao extrair conteúdo: {e}")
            self._usar_conteudo_simulado()
    
    def _extrair_conteudo_pdf(self) -> None:
        """
        Extrai o conteúdo de um arquivo PDF.
        """
        # Tenta diferentes métodos de extração em ordem de preferência
        conteudo = self._extrair_com_pymupdf()
        if conteudo:
            self.conteudo = conteudo
            return
        
        conteudo = self._extrair_com_pdfplumber()
        if conteudo:
            self.conteudo = conteudo
            return
        
        # Fallback: conteúdo simulado para demonstração
        self._usar_conteudo_simulado()
    
    def _extrair_conteudo_web(self) -> None:
        """
        Extrai o conteúdo de uma página web.
        """
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # Configuração da requisição
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            logger.info(f"Fazendo requisição para: {self.fonte}")
            response = requests.get(self.fonte, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse do HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts e estilos
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extrai texto
            texto = soup.get_text()
            
            # Limpa o texto
            linhas = (linha.strip() for linha in texto.splitlines())
            chunks = (frase.strip() for linha in linhas for frase in linha.split("  "))
            texto_limpo = ' '.join(chunk for chunk in chunks if chunk)
            
            if texto_limpo:
                self.conteudo = texto_limpo
                logger.info(f"Conteúdo web extraído: {len(self.conteudo)} caracteres")
            else:
                logger.warning("Não foi possível extrair texto da página web")
                self._usar_conteudo_simulado()
                
        except ImportError:
            logger.error("requests ou beautifulsoup4 não instalados. Instale com: pip install requests beautifulsoup4")
            self._usar_conteudo_simulado()
        except Exception as e:
            logger.error(f"Erro ao extrair conteúdo web: {e}")
            self._usar_conteudo_simulado()
    
    def _extrair_com_pymupdf(self) -> Optional[str]:
        """
        Tenta extrair conteúdo usando PyMuPDF (fitz).
        
        Returns:
            Optional[str]: Conteúdo extraído ou None se falhar
        """
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(self.fonte)
            
            # Verifica se o PDF está criptografado
            if doc.needs_pass:
                logger.warning("PDF está criptografado. Tentando extrair sem senha...")
                try:
                    doc.authenticate("")  # Tenta sem senha
                except:
                    logger.error("PDF criptografado e não foi possível descriptografar")
                    doc.close()
                    return None
            
            # Extrai texto de todas as páginas
            conteudos_paginas = []
            total_paginas = len(doc)
            
            logger.info(f"Iniciando extração com PyMuPDF: {total_paginas} páginas...")
            
            for i in range(total_paginas):
                try:
                    pagina = doc.load_page(i)
                    texto_pagina = pagina.get_text()
                    if texto_pagina:
                        conteudos_paginas.append(texto_pagina)
                    
                    # Log de progresso a cada 10 páginas
                    if (i + 1) % 10 == 0 or (i + 1) == total_paginas:
                        logger.info(f"Página {i + 1}/{total_paginas} processada")
                        
                except Exception as e:
                    logger.warning(f"Erro ao extrair página {i + 1}: {e}")
                    continue
            
            doc.close()
            
            # Junta todo o conteúdo
            conteudo = " ".join(conteudos_paginas)
            conteudo = re.sub(r'\s+', ' ', conteudo).strip()
            
            if conteudo:
                logger.info(f"Conteúdo extraído com PyMuPDF: {len(conteudo)} caracteres")
                return conteudo
            else:
                logger.warning("PyMuPDF não conseguiu extrair texto do PDF")
                return None
                
        except ImportError:
            logger.info("PyMuPDF não está instalado")
            return None
        except Exception as e:
            logger.error(f"Erro ao extrair com PyMuPDF: {e}")
            return None
    
    def _extrair_com_pdfplumber(self) -> Optional[str]:
        """
        Returns:
            Optional[str]: Conteúdo extraído ou None se falhar
        """
        try:
            import pdfplumber
            
            with pdfplumber.open(self.fonte) as pdf:
                conteudos_paginas = []
                total_paginas = len(pdf.pages)
                
                logger.info(f"Iniciando extração com pdfplumber: {total_paginas} páginas...")
                
                for i, pagina in enumerate(pdf.pages, 1):
                    try:
                        texto_pagina = pagina.extract_text()
                        if texto_pagina:
                            conteudos_paginas.append(texto_pagina)
                        
                        # Log de progresso a cada 10 páginas
                        if i % 10 == 0 or i == total_paginas:
                            logger.info(f"Página {i}/{total_paginas} processada")
                            
                    except Exception as e:
                        logger.warning(f"Erro ao extrair página {i}: {e}")
                        continue
                
                # Junta todo o conteúdo
                conteudo = " ".join(conteudos_paginas)
                conteudo = re.sub(r'\s+', ' ', conteudo).strip()
                
                if conteudo:
                    logger.info(f"Conteúdo extraído com pdfplumber: {len(conteudo)} caracteres")
                    return conteudo
                else:
                    logger.warning("pdfplumber não conseguiu extrair texto do PDF")
                    return None
                    
        except ImportError:
            logger.info("pdfplumber não está instalado")
            return None
        except Exception as e:
            logger.error(f"Erro ao extrair com pdfplumber: {e}")
            return None
    
    def _usar_conteudo_simulado(self) -> None:
        """
        Usa conteúdo simulado quando não é possível extrair da fonte real.
        """
        logger.warning("Usando conteúdo simulado - bibliotecas não disponíveis")
        
        if self.tipo_fonte == 'pdf':
            self.conteudo = """
            Este é um documento PDF de exemplo para análise. O documento contém informações importantes
            sobre análise documental e processamento de texto. A análise de frequência de palavras
            é uma técnica fundamental em processamento de linguagem natural.
            
            Palavras como "análise", "documento", "processamento" aparecem frequentemente neste texto.
            O objetivo é demonstrar como funciona a análise de frequência e ranking de palavras.
            
            Para extrair conteúdo real de PDFs, instale uma das bibliotecas:
            - pip install PyMuPDF (recomendado)
            - pip install pdfplumber
            - pip install PyPDF2 (último recurso)
            """
        else:
            self.conteudo = """
            Este é um conteúdo de página web de exemplo para análise. A página contém informações importantes
            sobre análise documental e processamento de texto. A análise de frequência de palavras
            é uma técnica fundamental em processamento de linguagem natural.
            
            Palavras como "análise", "documento", "processamento" aparecem frequentemente neste texto.
            O objetivo é demonstrar como funciona a análise de frequência e ranking de palavras.
            
            Para extrair conteúdo real de páginas web, instale:
            - pip install requests beautifulsoup4
            """
        
        logger.info(f"Conteúdo simulado criado: {len(self.conteudo)} caracteres")
    
    def obter_informacoes_fonte(self) -> Dict[str, any]:
        """
        Retorna informações detalhadas sobre a fonte (PDF ou web).
        
        Returns:
            Dict[str, any]: Dicionário com informações da fonte
        """
        return self.info_fonte
    
    def _processar_palavras(self) -> None:
        """
        Processa e limpa as palavras do conteúdo extraído.
        Remove pontuação, converte para minúsculas e filtra palavras comuns.
        """
        # Detecta idioma se não foi especificado
        if not self.idioma_detectado:
            self.idioma_detectado = self.stop_words_manager.detect_language(self.conteudo)
            logger.info(f"Idioma detectado: {self.idioma_detectado}")
        
        # Obtém stop words para o idioma detectado
        stop_words = self.stop_words_manager.get_stop_words(self.idioma_detectado)
        
        # Limpeza e processamento do texto
        texto_limpo = re.sub(r'[^\w\s]', '', self.conteudo.lower())
        palavras = texto_limpo.split()
        
        # Filtra palavras comuns e palavras muito curtas
        self.palavras_processadas = [
            palavra for palavra in palavras 
            if palavra not in stop_words and len(palavra) > 2
        ]
        
        logger.info(f"Processadas {len(self.palavras_processadas)} palavras úteis (idioma: {self.idioma_detectado})")
    
    def analisar_frequencia_palavras(self, top_n: int = 20) -> List[Tuple[str, int]]:
        """
        Analisa as palavras mais frequentes no documento e retorna um ranking.
        
        Args:
            top_n (int): Número de palavras mais frequentes a retornar
            
        Returns:
            List[Tuple[str, int]]: Lista de tuplas (palavra, frequência) ordenada por frequência
            
        Raises:
            ValueError: Se não houver palavras processadas
        """
        if not self.palavras_processadas:
            raise ValueError("Nenhuma palavra processada disponível para análise")
        
        # Conta a frequência das palavras
        contador = Counter(self.palavras_processadas)
        
        # Retorna as top_n palavras mais frequentes
        ranking = contador.most_common(top_n)
        
        logger.info(f"Análise de frequência concluída. Top {top_n} palavras identificadas")
        return ranking
    
    def obter_estatisticas_gerais(self) -> Dict[str, any]:
        """
        Retorna estatísticas gerais sobre o documento.
        
        Returns:
            Dict[str, any]: Dicionário com estatísticas do documento
        """
        total_palavras = len(self.palavras_processadas)
        palavras_unicas = len(set(self.palavras_processadas))
        
        # Calcula densidade de palavras únicas
        densidade = (palavras_unicas / total_palavras * 100) if total_palavras > 0 else 0
        
        estatisticas = {
            'total_palavras': total_palavras,
            'palavras_unicas': palavras_unicas,
            'densidade_vocabulario': round(densidade, 2),
            'tamanho_conteudo': len(self.conteudo),
            'fonte': self.fonte,
            'tipo_fonte': self.tipo_fonte,
            'idioma_detectado': self.idioma_detectado
        }
        
        logger.info("Estatísticas gerais calculadas")
        return estatisticas
    
    def analisar_com_chatgpt(self, prompt: str) -> Optional[str]:
        """
        Envia o conteúdo do documento para análise via API da OpenAI ChatGPT.
        
        Args:
            prompt (str): Prompt específico para enviar junto com o conteúdo
            
        Returns:
            Optional[str]: Resposta da API ou None se houver erro
            
        Raises:
            ValueError: Se a API key não estiver configurada
            ImportError: Se a biblioteca requests não estiver instalada
        """
        if not self.api_key:
            raise ValueError("API key da OpenAI não configurada. Configure OPENAI_API_KEY ou passe no construtor.")
        
        # Verifica se requests está disponível
        try:
            import requests
        except ImportError:
            raise ImportError(
                "Biblioteca 'requests' não está instalada. "
                "Para usar a funcionalidade ChatGPT, instale com: pip install requests"
            )
        
        try:
            # Preparação da requisição para a API da OpenAI
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Monta o prompt completo com o conteúdo do documento
            prompt_completo = f"""
            {prompt}
            
            Conteúdo da fonte ({self.tipo_fonte}):
            {self.conteudo[:4000]}  # Limita a 4000 caracteres para evitar tokens excessivos
            """
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt_completo
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            # Faz a requisição para a API
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            # Extrai a resposta
            resultado = response.json()
            resposta = resultado['choices'][0]['message']['content']
            
            logger.info("Análise com ChatGPT concluída com sucesso")
            return resposta
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para API da OpenAI: {e}")
            return None
        except KeyError as e:
            logger.error(f"Erro ao processar resposta da API: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado na análise com ChatGPT: {e}")
            return None
    
    def gerar_relatorio_completo(self, top_n: int = 25) -> str:
        """
        Gera um relatório completo com todas as análises disponíveis.
        
        Args:
            top_n (int): Número de palavras mais frequentes para incluir
            
        Returns:
            str: Relatório formatado com todas as análises
        """
        relatorio = []
        relatorio.append("=" * 80)
        relatorio.append("RELATÓRIO DE ANÁLISE DOCUMENTAL")
        relatorio.append("=" * 80)
        
        # Informações da fonte
        info = self.obter_informacoes_fonte()
        relatorio.append("INFORMAÇÕES DA FONTE:")
        
        if self.tipo_fonte == 'pdf':
            relatorio.append(f"- Tipo: {info['tipo']}")
            relatorio.append(f"- Nome: {info['nome']}")
            relatorio.append(f"- Caminho: {info['caminho_completo']}")
            relatorio.append(f"- Tamanho: {self._formatar_tamanho(info['tamanho_bytes'])}")
            relatorio.append(f"- Data de modificação: {info['data_modificacao']}")
            relatorio.append(f"- Total de páginas: {info['total_paginas']}")
            relatorio.append(f"- Versão PDF: {info['versao_pdf']}")
            relatorio.append(f"- Criptografado: {'Sim' if info['criptografado'] else 'Não'}")
        else:
            relatorio.append(f"- Tipo: {info['tipo']}")
            relatorio.append(f"- URL: {info['url']}")
            relatorio.append(f"- Título: {info['titulo']}")
            relatorio.append(f"- Tamanho: {self._formatar_tamanho(info['tamanho_bytes'])}")
            relatorio.append(f"- Data de acesso: {info['data_acesso']}")
            relatorio.append(f"- Status: {info['status_code']}")
            relatorio.append(f"- Content-Type: {info['content_type']}")
            relatorio.append(f"- Encoding: {info['encoding']}")
        
        # Metadados se disponíveis
        if info['metadados']:
            relatorio.append("")
            relatorio.append("METADADOS:")
            for chave, valor in info['metadados'].items():
                if valor and valor != 'Não informado':
                    relatorio.append(f"- {chave.replace('_', ' ').title()}: {valor}")
        
        relatorio.append("")
        
        # Estatísticas gerais
        stats = self.obter_estatisticas_gerais()
        relatorio.append("ESTATÍSTICAS GERAIS:")
        relatorio.append(f"- Total de palavras: {stats['total_palavras']:,}")
        relatorio.append(f"- Palavras únicas: {stats['palavras_unicas']:,}")
        relatorio.append(f"- Densidade de vocabulário: {stats['densidade_vocabulario']}%")
        relatorio.append(f"- Tamanho do conteúdo: {stats['tamanho_conteudo']:,} caracteres")
        relatorio.append(f"- Idioma detectado: {stats['idioma_detectado']}")
        relatorio.append("")
        
        # Ranking de palavras mais frequentes
        relatorio.append(f"TOP {top_n} PALAVRAS MAIS FREQUENTES:")
        ranking = self.analisar_frequencia_palavras(top_n)
        for i, (palavra, frequencia) in enumerate(ranking, 1):
            relatorio.append(f"{i:2d}. {palavra:<25} - {frequencia:5d} ocorrências")
        
        relatorio.append("")
        relatorio.append("=" * 80)
        
        return "\n".join(relatorio)
    
    def _formatar_tamanho(self, bytes_size: int) -> str:
        """
        Formata o tamanho em bytes para uma representação legível.
        
        Args:
            bytes_size (int): Tamanho em bytes
            
        Returns:
            str: Tamanho formatado (ex: "1.5 MB")
        """
        for unidade in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unidade}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"


def main():
    """
    Função principal para demonstração do uso da classe AnalisadorDocumental.
    """
    try:
        # Exemplo de uso da classe
        print("=== DEMONSTRAÇÃO DO ANALISADOR DOCUMENTAL ===\n")
        
        # Exemplo 1: Análise de PDF
        print("--- ANÁLISE DE PDF ---")
        analisador_pdf = AnalisadorDocumental("C:/Users/matol/Downloads/PBIA - IA_para_o_Bem_de_Todos.pdf")
        print(analisador_pdf.gerar_relatorio_completo())
        
        print("\n" + "="*80 + "\n")
        
        # Exemplo 2: Análise de página web
        print("--- ANÁLISE DE PÁGINA WEB ---")
        analisador_web = AnalisadorDocumental("https://www.softwareimprovementgroup.com/us-ai-legislation-overview/")
        print(analisador_web.gerar_relatorio_completo())
        
        # Exemplo de análise com ChatGPT (requer API key configurada)
        # api_key = "sua_api_key_aqui"  # Configure sua API key
        # analisador_chatgpt = AnalisadorDocumental("documento_exemplo.pdf", api_key)
        # 
        # prompt = "Analise este documento e identifique os principais tópicos discutidos."
        # resposta = analisador_chatgpt.analisar_com_chatgpt(prompt)
        # if resposta:
        #     print("\n=== ANÁLISE COM CHATGPT ===")
        #     print(resposta)
        
    except Exception as e:
        print(f"Erro na execução: {e}")


if __name__ == "__main__":
    main()