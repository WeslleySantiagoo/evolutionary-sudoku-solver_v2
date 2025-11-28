from tkinter import Label, Entry, Button, Toplevel, StringVar, LEFT, BOTH, W
from tkinter.ttk import Frame
import random
import numpy as np
from core import config


class ConfigWindow(Toplevel):
    """Janela de configuração para parâmetros do algoritmo genético."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configurações do Algoritmo Genético")
        self.geometry("500x600")
        self.resizable(False, False)

        # Centralizar janela
        self.transient(parent)
        self.grab_set()

        # Variáveis de configuração
        self.config_vars = {}

        # Frame principal com scroll
        main_frame = Frame(self, padding="20")
        main_frame.pack(fill=BOTH, expand=True)

        # Título
        title_label = Label(main_frame, text="Configurações do Algoritmo Genético",
                            font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))

        # Frame para os campos de configuração
        config_frame = Frame(main_frame)
        config_frame.pack(fill=BOTH, expand=True)

        # Criar campos para cada configuração
        self._create_config_field(config_frame, "POPULATION_SIZE",
                                  "Tamanho da População:",
                                  config.POPULATION_SIZE,
                                  "int", 0)

        self._create_config_field(config_frame, "ELITE_PERCENTAGE",
                                  "Percentual de Elite:",
                                  config.ELITE_PERCENTAGE,
                                  "float", 1)

        self._create_config_field(config_frame, "MAX_GENERATIONS",
                                  "Máximo de Gerações:",
                                  config.MAX_GENERATIONS,
                                  "int", 2)

        Label(config_frame, text="").grid(row=3, column=0, columnspan=2, pady=10)

        Label(config_frame, text="Parâmetros de Mutação",
              font=("Arial", 11, "bold")).grid(row=4, column=0, columnspan=2,
                                               pady=(0, 10))

        self._create_config_field(config_frame, "INITIAL_MUTATION_RATE",
                                  "Taxa de Mutação Inicial:",
                                  config.INITIAL_MUTATION_RATE,
                                  "float", 5)

        self._create_config_field(config_frame, "MIN_MUTATION_RATE",
                                  "Taxa de Mutação Mínima:",
                                  config.MIN_MUTATION_RATE,
                                  "float", 6)

        self._create_config_field(config_frame, "MAX_MUTATION_RATE",
                                  "Taxa de Mutação Máxima:",
                                  config.MAX_MUTATION_RATE,
                                  "float", 7)

        self._create_config_field(config_frame, "MEDIAN_FITNESS_UPPER_BOUND_RATIO",
                                  "Limite Superior da Aptidão Mediana:",
                                  config.MEDIAN_FITNESS_UPPER_BOUND_RATIO,
                                  "float", 8)

        self._create_config_field(config_frame, "MEDIAN_FITNESS_LOWER_BOUND_RATIO",
                                  "Limite Inferior da Aptidão Mediana:",
                                  config.MEDIAN_FITNESS_LOWER_BOUND_RATIO,
                                  "float", 9)

        self._create_config_field(config_frame, "MUTATION_RATE_ADJUSTMENT_STEP",
                                  "Passo de Ajuste da Taxa de Mutação:",
                                  config.MUTATION_RATE_ADJUSTMENT_STEP,
                                  "float", 10)

        Label(config_frame, text="").grid(row=11, column=0, columnspan=2, pady=10)

        self._create_config_field(config_frame, "RANDOM_SEED",
                                  "Semente Aleatória:",
                                  config.RANDOM_SEED,
                                  "int", 12)

        # Frame para os botões
        button_frame = Frame(main_frame)
        button_frame.pack(pady=(20, 0))

        # Botões
        Button(button_frame, text="Salvar", command=self._save_config,
               width=15).pack(side=LEFT, padx=5)
        Button(button_frame, text="Restaurar Padrão", command=self._restore_defaults,
               width=15).pack(side=LEFT, padx=5)
        Button(button_frame, text="Cancelar", command=self.destroy,
               width=15).pack(side=LEFT, padx=5)

    def _create_config_field(self, parent, var_name, label_text, default_value,
                             value_type, row):
        """Cria um campo de configuração."""
        label = Label(parent, text=label_text)
        label.grid(row=row, column=0, sticky=W, padx=5, pady=5)

        var = StringVar(value=str(default_value))
        self.config_vars[var_name] = (var, value_type)

        entry = Entry(parent, textvariable=var, width=30)
        entry.grid(row=row, column=1, sticky=W, padx=5, pady=5)

    def _validate_and_get_values(self):
        """Valida e retorna os valores das configurações."""
        values = {}
        try:
            for var_name, (var, value_type) in self.config_vars.items():
                value_str = var.get().strip()
                if value_type == "int":
                    values[var_name] = int(value_str)
                elif value_type == "float":
                    values[var_name] = float(value_str)
            return values
        except ValueError:
            return None

    def _save_config(self):
        """Salva as configurações no módulo config."""
        values = self._validate_and_get_values()
        if values is None:
            self._show_error("Erro de validação. Verifique se todos os valores estão corretos.")
            return

        # Validações adicionais
        if values["POPULATION_SIZE"] <= 0:
            self._show_error("Tamanho da população deve ser maior que 0.")
            return

        if not (0 < values["ELITE_PERCENTAGE"] < 1):
            self._show_error("Percentual de elite deve estar entre 0 e 1.")
            return

        if values["MAX_GENERATIONS"] <= 0:
            self._show_error("Máximo de gerações deve ser maior que 0.")
            return

        if not (0 < values["MIN_MUTATION_RATE"] <= values["MAX_MUTATION_RATE"] < 1):
            self._show_error("Taxas de mutação inválidas. Verifique os valores.")
            return

        if not (0 < values["INITIAL_MUTATION_RATE"] <= values["MAX_MUTATION_RATE"]):
            self._show_error("Taxa de mutação inicial deve estar entre min e max.")
            return

        # Atualizar o módulo config
        for var_name, value in values.items():
            setattr(config, var_name, value)

        # Aplicar a nova seed se ela foi alterada
        if "RANDOM_SEED" in values and values["RANDOM_SEED"] is not None:
            random.seed(values["RANDOM_SEED"])
            np.random.seed(values["RANDOM_SEED"])

        self._show_success("Configurações salvas com sucesso!")
        self.destroy()

    def _restore_defaults(self):
        """Restaura os valores padrão do config.py."""
        # Recarregar o módulo config para obter os valores originais
        import importlib
        importlib.reload(config)

        defaults = {
            "POPULATION_SIZE": config.POPULATION_SIZE,
            "ELITE_PERCENTAGE": config.ELITE_PERCENTAGE,
            "MAX_GENERATIONS": config.MAX_GENERATIONS,
            "INITIAL_MUTATION_RATE": config.INITIAL_MUTATION_RATE,
            "MIN_MUTATION_RATE": config.MIN_MUTATION_RATE,
            "MAX_MUTATION_RATE": config.MAX_MUTATION_RATE,
            "MEDIAN_FITNESS_UPPER_BOUND_RATIO": config.MEDIAN_FITNESS_UPPER_BOUND_RATIO,
            "MEDIAN_FITNESS_LOWER_BOUND_RATIO": config.MEDIAN_FITNESS_LOWER_BOUND_RATIO,
            "MUTATION_RATE_ADJUSTMENT_STEP": config.MUTATION_RATE_ADJUSTMENT_STEP,
            "RANDOM_SEED": config.RANDOM_SEED
        }

        for var_name, default_value in defaults.items():
            if var_name in self.config_vars:
                var, _ = self.config_vars[var_name]
                var.set(str(default_value))

    def _show_error(self, message):
        """Mostra uma mensagem de erro."""
        error_window = Toplevel(self)
        error_window.title("Erro")
        error_window.geometry("300x100")
        error_window.resizable(False, False)
        error_window.transient(self)
        error_window.grab_set()

        Label(error_window, text=message, wraplength=250).pack(pady=20)
        Button(error_window, text="OK", command=error_window.destroy).pack()

    def _show_success(self, message):
        """Mostra uma mensagem de sucesso."""
        success_window = Toplevel(self)
        success_window.title("Sucesso")
        success_window.geometry("300x100")
        success_window.resizable(False, False)
        success_window.transient(self)
        success_window.grab_set()

        Label(success_window, text=message, wraplength=250).pack(pady=20)
        Button(success_window, text="OK", command=success_window.destroy).pack()
