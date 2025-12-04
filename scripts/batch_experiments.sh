#!/bin/bash

###############################################################################
#
# batch_experiments.sh
#
# Script para executar múltiplos experimentos de resolução de Sudoku em lote.
#
# Uso:
#   ./batch_experiments.sh <puzzle_name> <num_attempts> <--with-pp|--without-pp>
#
# Exemplos:
#   ./batch_experiments.sh s01a 20 --without-pp
#   ./batch_experiments.sh s01b 15 --with-pp
#
# O script executará o número especificado de tentativas com a mesma configuração,
# usando sementes aleatórias para cada execução. Se o número de tentativas for
# maior que 10, executará em lotes de 10.
#
# Os resultados são salvos em results/ como um arquivo CSV com:
#  - Número da tentativa
#  - Nome do puzzle
#  - Configuração de pré-processamento
#  - Semente aleatória usada
#  - Se foi resolvido
#  - Tempo de execução
#  - Código de retorno
#
###############################################################################

set -e  # Sair se qualquer comando falhar

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Obter diretório do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Função para exibir mensagens
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Função para exibir uso
show_usage() {
    cat << EOF
Uso: $0 <puzzle_name> <num_attempts> <--with-pp|--without-pp>

Argumentos:
  puzzle_name      Nome do puzzle (ex: s01a, s01b, s02c)
  num_attempts     Número de vezes que será executado (ex: 20)
  preprocessing    --with-pp para com pré-processamento
                   --without-pp para sem pré-processamento

Exemplos:
  $0 s01a 20 --without-pp
  $0 s01b 15 --with-pp
  $0 s02a 5 --without-pp

Notas:
  - A semente sempre será aleatória (gerada a cada execução)
  - Se num_attempts > 10, executará em lotes de 10
  - Resultados são salvos em: results/
  - Cada resultado inclui: tempo, semente, status, etc.

EOF
}

# Validar argumentos
if [[ $# -lt 3 ]]; then
    log_error "Número incorreto de argumentos"
    show_usage
    exit 1
fi

PUZZLE_NAME="$1"
NUM_ATTEMPTS="$2"
PREPROCESSING="$3"

# Validar número de tentativas
if ! [[ "$NUM_ATTEMPTS" =~ ^[0-9]+$ ]] || [ "$NUM_ATTEMPTS" -lt 1 ]; then
    log_error "Número de tentativas deve ser um inteiro positivo: $NUM_ATTEMPTS"
    exit 1
fi

# Validar flag de pré-processamento
if [[ "$PREPROCESSING" != "--with-pp" ]] && [[ "$PREPROCESSING" != "--without-pp" ]]; then
    log_error "Flag de pré-processamento inválida: $PREPROCESSING"
    log_info "Use: --with-pp ou --without-pp"
    show_usage
    exit 1
fi

# Verificar se o puzzle existe
PUZZLE_PATH="$ROOT_DIR/puzzles/mantere_collection/${PUZZLE_NAME}.txt"
if [ ! -f "$PUZZLE_PATH" ]; then
    log_error "Puzzle não encontrado: $PUZZLE_NAME"
    log_info "Caminho procurado: $PUZZLE_PATH"
    exit 1
fi

# Verificar se o script Python existe
PYTHON_SCRIPT="$ROOT_DIR/scripts/batch_runner.py"
if [ ! -f "$PYTHON_SCRIPT" ]; then
    log_error "Script Python não encontrado: $PYTHON_SCRIPT"
    exit 1
fi

# Criar diretório de resultados
mkdir -p "$ROOT_DIR/results"

# Informações da execução
PP_DISPLAY="com pré-processamento"
if [[ "$PREPROCESSING" == "--without-pp" ]]; then
    PP_DISPLAY="sem pré-processamento"
fi

log_info "=========================================="
log_info "Batch Experiments - Solucionador Sudoku"
log_info "=========================================="
log_info "Puzzle: $PUZZLE_NAME"
log_info "Tentativas: $NUM_ATTEMPTS"
log_info "Configuração: $PP_DISPLAY"
log_info "Semente: aleatória (random)"
log_info ""
log_info "Executando script Python..."
log_info "=========================================="
echo

# Encontrar o python do venv se existir
PYTHON_CMD="python3"
if [ -f "$ROOT_DIR/.venv/bin/python" ]; then
    PYTHON_CMD="$ROOT_DIR/.venv/bin/python"
fi

# Executar o script Python
"$PYTHON_CMD" "$PYTHON_SCRIPT" "$PUZZLE_NAME" "$NUM_ATTEMPTS" "$PREPROCESSING"

if [ $? -eq 0 ]; then
    log_success "Experimentos concluídos com sucesso!"
    log_info "Verifique os resultados em: $ROOT_DIR/results/"
else
    log_error "Erro ao executar experimentos"
    exit 1
fi
