import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QMessageBox, QTreeWidgetItem
from ui_main import Ui_MainWindow
from database import DataBase

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.Pages.setCurrentWidget(self.ui.pg_home)

        # Navegação
        self.ui.btn_home.clicked.connect(lambda: self.ui.Pages.setCurrentWidget(self.ui.pg_home))
        self.ui.btn_tables.clicked.connect(lambda: self.ui.Pages.setCurrentWidget(self.ui.pg_table))
        self.ui.btn_contato.clicked.connect(lambda: self.ui.Pages.setCurrentWidget(self.ui.pg_contato))
        self.ui.btn_sobre.clicked.connect(lambda: self.ui.Pages.setCurrentWidget(self.ui.pg_sobre))
        self.ui.btn_pg_cadastro.clicked.connect(lambda: self.ui.Pages.setCurrentWidget(self.ui.pg_cadastro))
        self.ui.btn_pg_import.clicked.connect(lambda: self.ui.Pages.setCurrentWidget(self.ui.pg_import))

        # Botões
        self.ui.btn_cadastra_produto.clicked.connect(self.ir_para_pg_cadastro)
        self.ui.btn_cds.clicked.connect(self.cadastrar_produto)
        self.ui.btn_gerar.clicked.connect(self.gerar_saida)
        self.ui.btn_estorno.clicked.connect(self.estornar_produto)

        self.carregar_estoque()

        # Evento de clique duplo na árvore de produtos
        self.ui.tw_estoque.itemDoubleClicked.connect(self.on_item_double_click)

    def ir_para_pg_cadastro(self):
        """Vai para a página de cadastro de produtos"""
        if hasattr(self.ui, 'pg_CadastraProduto'):
            self.ui.Pages.setCurrentWidget(self.ui.pg_CadastraProduto)
        else:
            QMessageBox.warning(self, "Erro", "Página pg_CadastraProduto não encontrada!")

    def cadastrar_produto(self):
        """Cadastra um produto no banco de dados."""
        campos = [
            "txt_nfe", "txt_serie_2", "txt_emissao_2", "txt_chave_2",
            "txt_cnpj_2", "txt_emitente_2", "txt_total_2", "lineEdit_item",
            "txt_cod_item", "txt_descricao", "txt_medida", "txt_valor",
            "txt_data", "txt_Quantidade"
        ]

        valores = []
        for nome in campos:
            widget = getattr(self.ui, nome, None)  # Acessa diretamente o widget pela string do nome
            if widget is None:
                QMessageBox.warning(self, "Erro", f"Campo {nome} não encontrado na interface!")
                return
            text = widget.text().strip()
            if not text:
                QMessageBox.warning(self, "Erro", f"Preencha o campo {nome}!")
                return
            valores.append(text)

        db = DataBase()
        db.conecta()
        try:
            db.insert_produto(valores)  # Corrigido para passar corretamente os valores
            QMessageBox.information(self, "Sucesso", "Produto cadastrado!")
        except Exception as e:
            QMessageBox.critical(self, "Erro ao salvar", str(e))
        finally:
            db.close()

        # Limpa campos após cadastro
        for nome in campos:
            widget = getattr(self.ui, nome, None)
            if widget:
                widget.clear()

        self.carregar_estoque()
        self.ui.Pages.setCurrentWidget(self.ui.pg_table)

    def carregar_estoque(self):
        """Carrega todos os produtos no estoque na interface"""
        db = DataBase()
        db.conecta()
        rows = db.fetch_estoque()
        db.close()

        tw = self.ui.tw_estoque
        tw.clear()
        for row in rows:
            QTreeWidgetItem(tw, [str(v) for v in row])
        tw.expandAll()

    def gerar_saida(self):
        """Gera a saída de um produto e move para a tabela de saídas"""
        item = self.ui.tw_estoque.currentItem()
        if not item:
            QMessageBox.warning(self, "Erro", "Selecione um produto para gerar saída!")
            return

        id_produto = item.text(0)
        descricao = item.text(10)
        quantidade = item.text(13)

        db = DataBase()
        db.conecta()
        try:
            db.registrar_saida(id_produto, descricao, quantidade, "2025-05-06")  # Defina a data conforme necessário
            db.excluir_produto(id_produto)  # Exclui o produto da tabela estoque após gerar a saída
            QMessageBox.information(
                self, "Saída Gerada",
                f"Produto '{descricao}' com {quantidade} unidades saiu do estoque!"
            )
        except Exception as e:
            QMessageBox.critical(self, "Erro ao gerar saída", str(e))
        finally:
            db.close()

        self.carregar_estoque()

    def estornar_produto(self):
        """Estorna um produto do estoque"""
        item = self.ui.tw_estoque.currentItem()
        if not item:
            QMessageBox.warning(self, "Erro", "Selecione um produto para estornar!")
            return

        id_produto = item.text(0)
        descricao = item.text(10)

        confirmar = QMessageBox.question(
            self, "Confirmar Estorno",
            f"Tem certeza que deseja estornar o produto '{descricao}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmar == QMessageBox.Yes:
            db = DataBase()
            db.conecta()
            try:
                db.retorna_estoque(descricao,)  # Estorna o produto para o estoque
                db.excluir_saida(id_produto)  # Exclui a saída do banco de dados
                QMessageBox.information(self, "Sucesso", "Produto estornado do estoque!")
            except Exception as e:
                QMessageBox.critical(self, "Erro ao estornar", str(e))
            finally:
                db.close()
            self.carregar_estoque()

    def on_item_double_click(self, item):
        """Função chamada ao clicar duas vezes em um item da lista"""
        produto_id = item.text(0)
        descricao = item.text(10)

        # Excluir permanentemente o produto da tabela de estoque
        confirmar = QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Você tem certeza que deseja excluir o produto '{descricao}' permanentemente?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmar == QMessageBox.Yes:
            db = DataBase()
            db.conecta()
            try:
                db.excluir_produto(produto_id)  # Exclui o produto da tabela estoque
                QMessageBox.information(self, "Produto Excluído", f"Produto '{descricao}' excluído com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro ao excluir", str(e))
            finally:
                db.close()

        self.carregar_estoque()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


