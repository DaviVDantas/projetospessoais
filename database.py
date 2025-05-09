import sqlite3

class DataBase:
    def conecta(self):
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def criar_tabelas(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nfe TEXT,
                serie TEXT,
                emissao TEXT,
                chave TEXT,
                cnpj TEXT,
                emitente TEXT,
                total TEXT,
                item TEXT,
                cod_item TEXT,
                descricao TEXT,
                medida TEXT,
                valor TEXT,
                data TEXT,
                quantidade TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS saidas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_produto INTEGER,
                descricao TEXT,
                quantidade TEXT,
                data_saida TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE,
                senha TEXT,
                tipo TEXT
            )
        """)
        self.conn.commit()

    def insert_produto(self, valores):
        self.cursor.execute("""
            INSERT INTO produtos (nfe, serie, emissao, chave, cnpj, emitente, total, item, cod_item, descricao, medida, valor, data, quantidade)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, valores)
        self.conn.commit()

    def fetch_estoque(self):
        self.cursor.execute("SELECT * FROM produtos")
        return self.cursor.fetchall()

    def excluir_produto(self, id_produto):
        self.cursor.execute("DELETE FROM produtos WHERE id = ?", (id_produto,))
        self.conn.commit()

    def gerar_saida(self, id_produto, descricao, quantidade, data_saida):
        self.cursor.execute("""
            INSERT INTO saidas (id_produto, descricao, quantidade, data_saida)
            VALUES (?, ?, ?, ?)
        """, (id_produto, descricao, quantidade, data_saida))
        self.conn.commit()

    def fetch_saidas(self):
        self.cursor.execute("SELECT * FROM saidas")
        return self.cursor.fetchall()

    def excluir_saida(self, id_saida):
        self.cursor.execute("DELETE FROM saidas WHERE id = ?", (id_saida,))
        self.conn.commit()

    def cadastrar_usuario(self, usuario, senha, tipo):
        self.cursor.execute("""
            INSERT INTO usuarios (usuario, senha, tipo) VALUES (?, ?, ?)
        """, (usuario, senha, tipo))
        self.conn.commit()

    def validar_login(self, usuario, senha):
        self.cursor.execute("""
            SELECT tipo FROM usuarios WHERE usuario = ? AND senha = ?
        """, (usuario, senha))
        return self.cursor.fetchone()

