from ctypes.wintypes import DOUBLE, INT
from msilib.schema import RadioButton, tables
from venv import create
from PyQt6 import uic,QtWidgets
import sys
from PyQt6.QtWidgets import  QApplication, QWidget,QPushButton,QLabel
import mysql.connector
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph,Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import locale


numero_id = 0

banco = mysql.connector.connect(
    #host="localhost",
    #user="root",
    #passwd="",
    #database="cadastro_produtos"
    host= '108.167.132.244',
    user='nycofi04_nico',
    password='coloque sua senha',
    database='nycofi04_banco1_nicofifer.com',
)
def editar_dados():
    global numero_id

    linha = segunda_tela.tableWidget.currentRow()
    print (linha) # 0
    cursor = banco.cursor()
    cursor.execute("SELECT id FROM produtos")
    dados_lidos = cursor.fetchall()
    print(dados_lidos) # [(2,), (3,), (4,)]
    valor_id = dados_lidos[linha][0]
    print(valor_id) # 2
    cursor.execute("SELECT * FROM produtos WHERE id="+ str(valor_id))
    produto = cursor.fetchall()
    tela_editar.show()

    tela_editar.lineEdit.setText(str(produto[0][0]))
    tela_editar.lineEdit_2.setText(str(produto[0][1]))
    tela_editar.lineEdit_3.setText(str(produto[0][2]))
    tela_editar.lineEdit_4.setText(str(produto[0][3]))
    tela_editar.lineEdit_5.setText(str(produto[0][4]))
    numero_id = valor_id


def salvar_valor_editado():
    global numero_id

    # ler dados do lineEdit
    codigo = tela_editar.lineEdit_2.text()
    descricao = tela_editar.lineEdit_3.text()
    preco = tela_editar.lineEdit_4.text()
    categoria = tela_editar.lineEdit_5.text()
    # atualizar os dados no banco
    cursor = banco.cursor()
    cursor.execute("UPDATE produtos SET codigo = '{}', descricao = '{}', preco = '{}', categoria ='{}' WHERE id = {}".format(codigo,descricao,preco,categoria,numero_id))
    banco.commit()
    #atualizar as janelas
    tela_editar.close()
    segunda_tela.close()
    chama_segunda_tela()

    

    
    
    
def excluir_dados():
    linha = segunda_tela.tableWidget.currentRow()
    segunda_tela.tableWidget.removeRow(linha)

    cursor = banco.cursor()
    cursor.execute("SELECT id FROM produtos")
    dados_lidos = cursor.fetchall()
    valor_id = dados_lidos[linha][0]
    cursor.execute("DELETE FROM produtos WHERE id="+ str(valor_id))
    cursor.execute("ALTER TABLE produtos AUTO_INCREMENT = 1")
    #exclusao = "DELETE FROM produto WHERE id = %s"
    #valor_para_excluir = (f"{valor_id}",)  # Adicione uma vírgula após o elemento
    #cursor.execute(exclusao, valor_para_excluir)
    banco.commit()
    

def formatar_preco(preco):
    # Defina a localização para o Brasil
    locale.setlocale(locale.LC_ALL, 'pt_BR.utf-8')
    return locale.currency(preco, grouping=True, symbol=None)

def gerar_pdf():
    cursor = banco.cursor()
    comando_SQL = "SELECT * FROM produtos"
    cursor.execute(comando_SQL)
    dados_lidos = cursor.fetchall()

    # Formata os preços no formato real brasileiro
    dados_formatados = []
    for linha in dados_lidos:
        linha_formatada = list(linha)
        linha_formatada[3] = formatar_preco(float(linha[3]))
        dados_formatados.append(linha_formatada)

    # Configuração do estilo de parágrafo para os cabeçalhos da tabela
    estilo_cabecalho = getSampleStyleSheet()["Normal"]
    estilo_cabecalho.alignment = 1  # Alinhamento central
    estilo_cabecalho.fontSize = 10
    estilo_cabecalho.textColor = colors.black  # Cor do texto dos cabeçalhos

    # Configuração do estilo de parágrafo para os dados da tabela
    estilo_dados = getSampleStyleSheet()["Normal"]
    estilo_dados.alignment = 1  # Alinhamento central
    estilo_dados.fontSize = 10
    estilo_dados.textColor = colors.black  # Cor do texto dos dados

    # Configuração do estilo de parágrafo para o título
    estilo_titulo = ParagraphStyle(name="estilo_titulo")
    estilo_titulo.fontSize = 18  # Aumenta o tamanho da fonte do título
    estilo_titulo.alignment = 1  # Alinhamento central
    estilo_titulo.textColor = colors.black  # Cor do texto do título
    estilo_titulo.leading = 50  # Adiciona um espaço na parte inferior

    # Criação do documento PDF
    doc = SimpleDocTemplate("cadastro_produtos.pdf", pagesize=letter)

    # Lista de elementos do PDF
    elementos = []

    # Título
    titulo = Paragraph("<b>*** AUTO PEÇAS NICOFIFER ***</b>", estilo_titulo)  # Negrito no título
    elementos.append(titulo)

     # Cabeçalhos da tabela
    cabecalhos = ["ID", "CÓDIGO", "PRODUTO", "PREÇO", "CATEGORIA"]

    # Valor total dos produtos
    valor_total_texto = "Total"
    total = sum(float(linha[3]) for linha in dados_lidos)

    # Formata o valor total como moeda brasileira
    valor_total_formatado = formatar_preco(total)

    # Adiciona cabeçalhos e dados formatados
    dados_formatados.insert(0, cabecalhos)

    # Determina o número de colunas na tabela
    num_colunas = len(cabecalhos)

    # Alinhamento das colunas
    alinhamento_colunas = [('ALIGN', (i, 0), (i, -1), 'LEFT') for i in range(num_colunas)]
    # Alinha a coluna "CÓDIGO" (índice 1) e a coluna "PREÇO" (índice 3) à direita
    alinhamento_colunas[1] = ('ALIGN', (1, 0), (1, -1), 'RIGHT')
    alinhamento_colunas[3] = ('ALIGN', (3, 0), (3, -1), 'RIGHT')

    # Tabela
    tabela = Table(dados_formatados, style=[
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Cor de fundo para a primeira linha (cabeçalhos)
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Cor do texto para a primeira linha
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black)  # Grossura da borda da tabela
    ] + alinhamento_colunas)
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Cor de fundo para linhas de dados alternadas
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),  # Cor do texto para linhas de dados
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Grossura da borda da tabela
    ]))

    elementos.append(tabela)

    # Espaço em branco
    elementos.append(Spacer(1, 12))

    # Adiciona o valor total formatado
    elementos.append(Paragraph(f"<b>{valor_total_texto}: R$ {valor_total_formatado}</b>", estilo_cabecalho))

    # Constrói o PDF
    doc.build(elementos)
    print("PDF FOI GERADO COM SUCESSO!")


# Certifique-se de que o módulo 'reportlab' esteja instalado antes de executar este código.


def funcao_principal():
    linha1 = formulario.lineEdit.text()
    linha2 = formulario.lineEdit_2.text().title()
    linha3 = formulario.lineEdit_3.text()

    categoria = ""
    
    if formulario.radioButton.isChecked() :
        print("Categoria SCANIA selecionada")
        categoria ="Scania"
        
    elif formulario.radioButton_2.isChecked() :
        print("Categoria VOLVO selecionada")
        
        categoria ="Volvo"
    else :
        print("Categoria IVECO selecionada")
        categoria ="Iveco"

    print("Codigo:",linha1)
    print("Descricao:",linha2)
    print("Preco",linha3)

    cursor = banco.cursor()
    comando_SQL = "INSERT INTO produtos (codigo,descricao,preco,categoria) VALUES (%s,%s,%s,%s)"
    dados = (str(linha1),str(linha2),str(linha3),categoria)
    cursor.execute(comando_SQL,dados)
    banco.commit()
    formulario.lineEdit.setText("")
    formulario.lineEdit_2.setText("")
    formulario.lineEdit_3.setText("")

def chama_segunda_tela():
    segunda_tela.show()

    cursor = banco.cursor()
    #comando_SQL = "SELECT * FROM produtos "
    comando_SQL = "SELECT * FROM produtos ORDER BY id;"
    cursor.execute(comando_SQL)
    dados_lidos = cursor.fetchall()

    segunda_tela.tableWidget.setRowCount(len(dados_lidos))
    segunda_tela.tableWidget.setColumnCount(5)

    for i in range(0, len(dados_lidos)):
        for j in range(0, 5):
           segunda_tela.tableWidget.setItem(i,j,QtWidgets.QTableWidgetItem(str(dados_lidos[i][j]))) 
   
     

  
        

app=QtWidgets.QApplication([])
formulario=uic.loadUi("formulario.ui")
segunda_tela=uic.loadUi("listar_dados.ui")
tela_editar=uic.loadUi("tela_editar.ui")
formulario.pushButton_1.clicked.connect(funcao_principal)
formulario.pushButton_2.clicked.connect(chama_segunda_tela)
segunda_tela.pushButton.clicked.connect(gerar_pdf)
segunda_tela.pushButton_2.clicked.connect(excluir_dados)
segunda_tela.pushButton_3.clicked.connect(editar_dados)
tela_editar.pushButton_1.clicked.connect(salvar_valor_editado)

formulario.show()
app.exec()

'''
use cadastro_produtos;
show tables;
describe produtos;
select * from produtos;

 ALTER TABLE produtos AUTO_INCREMENT = 1;


INSERT INTO produtos (codigo,descicao,preco,categoria) VALUES (123,"impressora",500.00,"informatica");

create table produtos(
    id INT NOT NULL AUTO_INCREMENT,
    codigo INT,
    descricao VARCHAR(50),
    preco DOUBLE,
    categoria VARCHAR(20),
    PRIMARY KEY (id)
);

'''
