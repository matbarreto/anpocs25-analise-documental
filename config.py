"""
Configuração e gerenciamento de stop words para o Analisador Documental.
"""

import json
import os
from typing import Set, Dict, List
import logging

logger = logging.getLogger(__name__)

class StopWordsManager:
    """
    Gerenciador de stop words para diferentes idiomas.
    """
    
    def __init__(self, config_file: str = "stop_words.json"):
        """
        Inicializa o gerenciador de stop words.
        
        Args:
            config_file (str): Caminho para o arquivo de configuração JSON
        """
        self.config_file = config_file
        self.stop_words_cache: Dict[str, Set[str]] = {}
        self._load_stop_words()
    
    def _load_stop_words(self) -> None:
        """
        Carrega as stop words do arquivo de configuração.
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    
                # Converte listas para sets para melhor performance
                for idioma, palavras in data.items():
                    self.stop_words_cache[idioma] = set(palavras)
                    
                logger.info(f"Stop words carregadas para {len(self.stop_words_cache)} idiomas")
            else:
                logger.warning(f"Arquivo de configuração não encontrado: {self.config_file}")
                self._create_default_config()
                
        except Exception as e:
            logger.error(f"Erro ao carregar stop words: {e}")
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """
        Cria configuração padrão se o arquivo não existir.
        """
        default_stop_words = {
            "portugues": [
                "a", "o", "e", "é", "de", "do", "da", "em", "um", "para", "com", "não", "uma",
                "os", "no", "se", "na", "por", "mais", "as", "dos", "como", "mas", "foi", "ele", "das"
            ],
            "ingles": [
                "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "he", "in", "is", "it", "its", "of", "on", "that", "the", "to", "was", "will", "with",
                "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves"
            ]
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as file:
                json.dump(default_stop_words, file, indent=2, ensure_ascii=False)
            
            # Carrega a configuração padrão
            for idioma, palavras in default_stop_words.items():
                self.stop_words_cache[idioma] = set(palavras)
                
            logger.info(f"Arquivo de configuração padrão criado: {self.config_file}")
            
        except Exception as e:
            logger.error(f"Erro ao criar configuração padrão: {e}")
            # Fallback com stop words básicas
            self.stop_words_cache = {
                "portugues": {"a", "o", "e", "de", "em", "um", "para", "com"},
                "ingles": {"a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "the", "to", "in", "is", "it"}
            }
    
    def get_stop_words(self, idioma: str = "portugues") -> Set[str]:
        """
        Retorna as stop words para um idioma específico.
        
        Args:
            idioma (str): Idioma das stop words ('portugues', 'ingles', 'espanhol')
            
        Returns:
            Set[str]: Conjunto de stop words
        """
        return self.stop_words_cache.get(idioma, set())
    
    def add_stop_words(self, idioma: str, palavras: List[str]) -> None:
        """
        Adiciona novas stop words para um idioma.
        
        Args:
            idioma (str): Idioma das stop words
            palavras (List[str]): Lista de palavras a adicionar
        """
        if idioma not in self.stop_words_cache:
            self.stop_words_cache[idioma] = set()
        
        self.stop_words_cache[idioma].update(palavras)
        logger.info(f"Adicionadas {len(palavras)} stop words para {idioma}")
    
    def remove_stop_words(self, idioma: str, palavras: List[str]) -> None:
        """
        Remove stop words de um idioma.
        
        Args:
            idioma (str): Idioma das stop words
            palavras (List[str]): Lista de palavras a remover
        """
        if idioma in self.stop_words_cache:
            self.stop_words_cache[idioma].difference_update(palavras)
            logger.info(f"Removidas {len(palavras)} stop words de {idioma}")
    
    def save_config(self) -> None:
        """
        Salva a configuração atual no arquivo JSON.
        """
        try:
            # Converte sets de volta para listas para serialização JSON
            config_data = {}
            for idioma, palavras_set in self.stop_words_cache.items():
                config_data[idioma] = sorted(list(palavras_set))
            
            with open(self.config_file, 'w', encoding='utf-8') as file:
                json.dump(config_data, file, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuração salva em: {self.config_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {e}")
    
    def get_available_languages(self) -> List[str]:
        """
        Retorna lista de idiomas disponíveis.
        
        Returns:
            List[str]: Lista de idiomas
        """
        return list(self.stop_words_cache.keys())
    
    def detect_language(self, texto: str) -> str:
        """
        Detecta o idioma do texto baseado nas palavras mais comuns.
        
        Args:
            texto (str): Texto para análise
            
        Returns:
            str: Idioma detectado ('portugues', 'ingles', 'espanhol')
        """
        # Palavras características de cada idioma
        indicadores = {
            "portugues": {"de", "da", "do", "em", "um", "uma", "para", "com", "não", "que", "se", "por", "mais", "as", "dos", "como", "mas", "foi", "ele", "das"},
            "ingles": {"the", "and", "of", "to", "a", "in", "is", "it", "you", "that", "he", "was", "for", "on", "are", "as", "with", "his", "they", "at"},
            "espanhol": {"de", "la", "el", "en", "y", "a", "los", "se", "del", "las", "un", "por", "con", "no", "una", "su", "para", "es", "al", "lo"}
        }
        
        # Converte texto para minúsculas e divide em palavras
        palavras = set(texto.lower().split())
        
        # Conta ocorrências de palavras características
        scores = {}
        for idioma, palavras_caracteristicas in indicadores.items():
            scores[idioma] = len(palavras.intersection(palavras_caracteristicas))
        
        # Retorna o idioma com mais palavras características
        if scores:
            return max(scores, key=scores.get)
        
        return "portugues"  # Padrão
