import random
import tkinter as tk
from tkinter import ttk
##import sqlite3
import mysql.connector
mysql.connector.locales = {'eng': 'en'}
from mysql.connector import Error
from datetime import datetime
from tkinter import simpledialog 
from tkinter import messagebox
from decimal import Decimal
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

# Função para conectar ao banco de dados (obs: devido o fato de ja ter feito a conecao do estoque antes de criar essa funcao optei por nao altera a funcao show_stock_window de estoque)
def conectar_banco():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='papelaria',
            user='?????????',
            password='?????????'
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Erro de Conexão", f"Erro ao conectar ao banco de dados: {err}")
        return None

def validate_number_input(P):
     # Aceitar apenas números, vírgulas e pontos para valor
     if P == "" or P.isdigit() or (P.count('.') <= 1 and P.count(',') <= 1 and P.replace('.', '').replace(',', '').isdigit()):
        return True
     return False

#-----Função para exibir a janela do status do caixa-----#
def gerar_pdf(id_caixa):
    # Conecta ao banco de dados e busca os dados do caixa específico
    conn = conectar_banco()
    if conn is None:
        return  # Sai da função se não conseguir conectar

    cursor = conn.cursor()

    # Modifica a consulta para buscar apenas pelo id_caixa especificado
    query = """
        SELECT data_caixa, saldo_inicial, total_vendas, total_dinheiro, total_pix, total_credito, total_debito 
        FROM caixa_dia 
        WHERE id_caixa = %s
    """
    cursor.execute(query, (id_caixa,))
    registro = cursor.fetchone()

    if registro:
        data_caixa, saldo_inicial, total_vendas, total_dinheiro, total_pix, total_credito, total_debito = registro

        # Formata a data do caixa para usar no nome do arquivo (formato: YYYY-MM-DD)
        data_formatada = data_caixa.strftime('%Y-%m-%d')
        destino_pdf = f"C:/Users/Paulo Vieira/OneDrive/Área de Trabalho/fechamento_do_dia_{data_formatada}.pdf"

        # Garante que o diretório existe
        diretorio = os.path.dirname(destino_pdf)
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)

        # Cria um objeto canvas para gerar o PDF
        pdf = canvas.Canvas(destino_pdf, pagesize=A4)

        # Adiciona as informações do caixa ao PDF
        y_position = 750  # Posição vertical inicial para o texto
        pdf.drawString(100, y_position, "Relatório do Caixa do Dia")
        y_position -= 20  # Espaço entre as linhas

        pdf.drawString(100, y_position, f"Data: {data_caixa}")
        y_position -= 15
        pdf.drawString(100, y_position, f"Saldo Inicial: R$ {saldo_inicial:.2f}")
        y_position -= 15
        pdf.drawString(100, y_position, f"Total Vendas: R$ {total_vendas:.2f}")
        y_position -= 15
        pdf.drawString(100, y_position, f"Total Dinheiro: R$ {total_dinheiro:.2f}")
        y_position -= 15
        pdf.drawString(100, y_position, f"Total Pix: R$ {total_pix:.2f}")
        y_position -= 15
        pdf.drawString(100, y_position, f"Total Crédito: R$ {total_credito:.2f}")
        y_position -= 15
        pdf.drawString(100, y_position, f"Total Débito: R$ {total_debito:.2f}")

        # Salva o documento PDF
        pdf.save()

        print(f"PDF gerado em: {destino_pdf}")
    else:
        messagebox.showwarning("Aviso", f"Nenhum registro encontrado para o id_caixa: {id_caixa}")

    # Fecha a conexão com o banco de dados
    cursor.close()
    conn.close()


    print(f"PDF gerado em: {destino_pdf}")

def caixa_status():
    # Configurações da janela de status do caixa
    caixa_window = tk.Toplevel(root)
    caixa_window.title("Status do Caixa")
    width = int(screen_width * 0.1)
    height = int(screen_height * 0.6)
    x_position = 0
    y_position = int(screen_height * 0.1)
    caixa_window.geometry(f"{width}x{height}+{x_position}+{y_position}")
    caixa_window.minsize(width, height)

    # Frame de status com barra indicativa
    status_frame = tk.Frame(caixa_window, bg="gray")
    status_frame.pack(expand=True, fill=tk.BOTH)
    status_bar = tk.Frame(status_frame, bg="red", height=50)
    status_bar.pack(fill=tk.X, padx=10, pady=(20, 10))
    status_label = tk.Label(status_bar, text="Status do Caixa: Fechado", font=("Arial", 20), fg="white", bg="red")
    status_label.pack(pady=10)

    # Configuração da parte inferior da janela
    bottom_frame = tk.Frame(status_frame, bg="gray")
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 30))
    saldo_entry = tk.Entry(bottom_frame, font=("Arial", 20), width=20)
    saldo_entry.pack(pady=(0, 5), ipady=7)
    saldo_entry.insert(0, "Digite o saldo inicial")

    # Função para limpar o texto padrão
    def limpar(event):
        if saldo_entry.get() == "Digite o saldo inicial":
            saldo_entry.delete(0, tk.END)

    saldo_entry.bind("<FocusIn>", limpar)

    # Função para verificar o status do caixa no banco de dados
    def verificar_status_caixa():
        conn = conectar_banco()
        if conn is None:
            return
        
        cursor = conn.cursor()
        try:
            # Verificar o maior id_caixa e o status atual
            cursor.execute("SELECT id_caixa, status FROM caixa_dia ORDER BY id_caixa DESC LIMIT 1")
            result = cursor.fetchone()

            if result is None or result[1] == 'fechado':
                status_label.config(text="Status do Caixa: Fechado", bg="red")
                status_bar.config(bg="red")
                preparar_caixa_fechado()  # Chama a função para caixa fechado
            else:
                status_label.config(text="Status do Caixa: Aberto", bg="green")
                status_bar.config(bg="green")
                preparar_caixa_aberto()  # Chama a função para caixa aberto
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao consultar o banco de dados: {err}")
        finally:
            cursor.close()
            conn.close()

    # Função para preparar o layout quando o caixa estiver fechado
    def preparar_caixa_fechado():
        # Exibe campo de saldo inicial para abrir o caixa
        saldo_entry.pack(pady=(0, 5), ipady=7)

        # Botão para abrir o caixa
        toggle_button = tk.Button(
            bottom_frame,
            text="Abrir Caixa",
            command=abrir_caixa,
            font=("Arial", 18),
            width=15,
            height=2
        )
        toggle_button.pack(pady=(30, 0))

    # Função para preparar o layout quando o caixa estiver aberto
    def preparar_caixa_aberto():
        saldo_entry.pack_forget()  # Esconde o campo de saldo, já que o caixa está aberto

        # Botão para abrir uma nova janela com detalhes do caixa
        toggle_button = tk.Button(
            bottom_frame,
            text="fechar caixa",
            command=abrir_janela_caixa_aberto,
            font=("Arial", 18),
            width=15,
            height=2
        )
        toggle_button.pack(pady=(30, 0))

    # Função para abrir o caixa (quando está fechado)
    def abrir_caixa():
        saldo_inicial = saldo_entry.get()

        # Verificar se o saldo inserido é válido
        try:
            saldo_inicial = float(saldo_inicial.replace(',', '.'))  # Converter para float
        except ValueError:
            messagebox.showerror("Erro", "Digite um valor válido para o saldo inicial.")
            return

        conn = conectar_banco()
        if conn is None:
            return
        
        cursor = conn.cursor()

        try:
            # Inserir novo registro no banco com status "aberto" e saldo inicial
            cursor.execute("""
                INSERT INTO caixa_dia (data_caixa, saldo_inicial, status)
                VALUES (CURDATE(), %s, 'aberto')
            """, (saldo_inicial,))
            conn.commit()
            messagebox.showinfo("Sucesso", "Caixa aberto com sucesso.")
            status_label.config(text="Status do Caixa: Aberto", bg="green")
            status_bar.config(bg="green")
            preparar_caixa_aberto()  # Atualiza o layout para "caixa aberto"
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao inserir no banco de dados: {err}")
        finally:
            cursor.close()
            conn.close()

    # Função para abrir uma nova janela com detalhes do caixa aberto
    def abrir_janela_caixa_aberto():
        # Nova janela para exibir os detalhes do caixa aberto
        detalhes_window = tk.Toplevel(root)
        detalhes_window.title("Detalhes do Caixa Aberto")
        
        # Dimensões da janela
        width = int(screen_width * 0.6)  # Janela mais larga
        height = int(screen_height * 0.5)
        x_position = int((screen_width - width) / 2)
        y_position = int((screen_height - height) / 2)
        detalhes_window.geometry(f"{width}x{height}+{x_position}+{y_position}")
        detalhes_window.minsize(width, height)

        # Frame principal para dividir a janela verticalmente
        main_frame = tk.Frame(detalhes_window)
        main_frame.pack(expand=True, fill=tk.BOTH)
        # Criando o lado esquerdo (80% da largura) com barra de rolagem
        left_frame = tk.Frame(main_frame, bg="lightblue", width=int(width * 0.8), height=height)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Criando um canvas para permitir a barra de rolagem
        canvas = tk.Canvas(left_frame, bg="lightblue")
        scrollbar = tk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="lightblue")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Empacotando o canvas e a scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Conectar ao banco de dados para buscar as vendas fechadas no dia de abertura do caixa
        conn = conectar_banco()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            
            # Consulta para obter a data de abertura do caixa atual
            cursor.execute("""
                SELECT data_caixa 
                FROM caixa_dia 
                WHERE status = 'aberto'
                ORDER BY id_caixa DESC
                LIMIT 1
            """)
            caixa_aberto = cursor.fetchone()

            if caixa_aberto:
                data_caixa_aberto = caixa_aberto[0]
                
                # Consulta para obter as vendas fechadas (venda_aberta = 'nao') no dia da abertura do caixa
                cursor.execute("""
                    SELECT nome, valor_total, forma_pagamento, data_venda 
                    FROM vendas 
                    WHERE venda_aberta = 'nao' 
                    AND DATE(data_venda) = %s
                """, (data_caixa_aberto,))
                
                vendas_fechadas = cursor.fetchall()
                 # Função para fechar o caixa
                def fechar_caixa():
                    # Conectar ao banco de dados para fechar o caixa aberto
                    conn = conectar_banco()
                    if conn is None:
                        return

                    try:
                        cursor = conn.cursor()
                        
                        # Atualizar o status do caixa aberto para 'fechado'
                        cursor.execute("""
                            UPDATE caixa_dia
                            SET status = 'fechado'
                            WHERE status = 'aberto'
                            ORDER BY id_caixa DESC
                            LIMIT 1
                        """)
                        conn.commit()

                      # Pega o ID do caixa que acabou de ser fechado
                        cursor.execute("SELECT id_caixa FROM caixa_dia WHERE status = 'fechado' ORDER BY id_caixa DESC LIMIT 1")
                        id_caixa = cursor.fetchone()[0]

                        # Gerar o PDF com os dados do caixa fechado
                        gerar_pdf(id_caixa)
                        # Exibir uma mensagem de confirmação
                        messagebox.showinfo("Sucesso", "O caixa foi fechado com sucesso e o PDF foi gerado.")

                        # Fechar a janela após fechar o caixa
                        detalhes_window.destroy()

                    except mysql.connector.Error as err:
                        messagebox.showerror("Erro", f"Erro ao fechar o caixa: {err}")
                    finally:
                        cursor.close()
                        conn.close()


                # Exibindo as vendas fechadas no lado esquerdo (80% da largura)
                left_label = tk.Label(scrollable_frame, text="Vendas Fechadas:", font=("Arial", 20), bg="lightblue")
                left_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

               
                if vendas_fechadas:
                    row = 1
                    col = 0
                    for venda in vendas_fechadas:
                        nome_venda, valor_total, forma_pagamento, data_venda = venda

                        # Criação do Label para exibir cada venda
                        venda_info = f"Venda: {nome_venda}\nValor: R$ {valor_total:.2f}\nPagamento: {forma_pagamento}\nData: {data_venda}"
                        venda_info_label = tk.Label(
                            scrollable_frame, 
                            text=venda_info,
                            font=("Arial", 12), 
                            bg="lightblue", 
                            relief=tk.RIDGE, 
                            padx=10, 
                            pady=10
                        )
                        venda_info_label.grid(row=row, column=col, padx=10, pady=10, sticky="w")
                        
                        col += 1
                        if col > 5:  # Limite de 5 colunas por linha
                            col = 0
                            row += 1
                else:
                    # Se não houver vendas fechadas no dia
                    no_vendas_label = tk.Label(scrollable_frame, text="Nenhuma venda fechada hoje.", font=("Arial", 12), bg="lightblue")
                    no_vendas_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

            else:
                # Se não houver caixa aberto
                no_caixa_label = tk.Label(scrollable_frame, text="Nenhum caixa aberto.", font=("Arial", 12), bg="lightblue")
                no_caixa_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao consultar o banco de dados: {err}")
        finally:
            cursor.close()
            conn.close()



        # Criando o lado direito (20% da largura)
        right_frame = tk.Frame(main_frame, bg="lightgray", width=int(width * 0.2), height=height)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)

        # Conectar ao banco de dados para buscar informações do caixa aberto
        conn = conectar_banco()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            # Consulta para obter as informações do caixa que está aberto
            cursor.execute("""
                SELECT saldo_inicial, total_vendas, total_dinheiro, total_pix, total_credito, total_debito
                FROM caixa_dia
                WHERE status = 'aberto'
                ORDER BY id_caixa DESC
                LIMIT 1
            """)
            caixa_aberto = cursor.fetchone()

            if caixa_aberto:
                saldo_inicial, total_vendas, total_dinheiro, total_pix, total_credito, total_debito = caixa_aberto
                
                # Exibindo as informações do caixa aberto no lado direito
                right_label = tk.Label(right_frame, text="Informações do Caixa Aberto:", font=("Arial", 20), bg="lightgray")
                right_label.pack(pady=20, padx=20)
                
                right_info_label = tk.Label(
                    right_frame,
                    text=(
                        f"Saldo Inicial: R$ {saldo_inicial:.2f}\n"
                        f"Total Vendas: R$ {total_vendas:.2f}\n"
                        f"Total Dinheiro: R$ {total_dinheiro:.2f}\n"
                        f"Total Pix: R$ {total_pix:.2f}\n"
                        f"Total Crédito: R$ {total_credito:.2f}\n"
                        f"Total Débito: R$ {total_debito:.2f}\n"
                        f"Saldo final: R$ {saldo_inicial + total_vendas:.2f}"
                    ),
                    font=("Arial", 12),
                    bg="lightgray"
                )
                right_info_label.pack(pady=10)

            else:
                # Caso não haja caixa aberto, exibir mensagem
                no_caixa_label = tk.Label(right_frame, text="Nenhum caixa está aberto.", font=("Arial", 12), bg="lightgray")
                no_caixa_label.pack(pady=20)

         
            # Adicionar o botão "Fechar" na parte inferior
            fechar_button = tk.Button(right_frame, text="Fechar Caixa", font=("Arial", 14), bg="red", fg="white", command=fechar_caixa)
            fechar_button.pack(side=tk.BOTTOM, pady=20)
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao consultar o banco de dados: {err}")
        finally:
            cursor.close()
            conn.close()



    # Verificar o status do caixa ao abrir a janela
    verificar_status_caixa()

#-----Função para mostrar a janela do estoque com a barra de busca e a tabela de itens-----#
def show_stock_window(existing_window=None):
    if existing_window:
        existing_window.destroy()  # Fecha a janela de estoque existente

    stock_window = tk.Toplevel(root)
    stock_window.title("Estoque")

    # Definindo as dimensões e posição da janela de estoque
    width = int(screen_width * 0.4)
    height = int(screen_height * 0.4)
    x_position = int((screen_width - width) / 2)
    y_position = int((screen_height - height) / 2)
    stock_window.geometry(f"{width}x{height}+{x_position}+{y_position}")
    stock_window.minsize(width, height)

    conn = conectar_banco()
    if conn is None:
        return None

    try:
        cursor = conn.cursor()

        # Busca inicial dos itens
        cursor.execute("SELECT codigo, nome, valor FROM estoque")
        items = cursor.fetchall()

        # Função para filtrar itens com base na busca
        def search_items():
            query = search_entry.get().lower()
            filtered_items = [item for item in items if query in item[1].lower()]
            update_item_list(filtered_items)

        # Função para atualizar a lista de itens exibidos
        def update_item_list(filtered_items):
            # Limpar os dados anteriores da tabela
            for widget in table_frame.winfo_children():
                widget.destroy()

            # Cabeçalhos da tabela
            tk.Label(table_frame, text="Código", font=("Arial", 16, "bold")).grid(row=0, column=0, padx=30, pady=10)
            tk.Label(table_frame, text="Nome", font=("Arial", 16, "bold")).grid(row=0, column=1, padx=30, pady=10)
            tk.Label(table_frame, text="Valor (R$)", font=("Arial", 16, "bold")).grid(row=0, column=2, padx=30, pady=10)

            # Adiciona os itens filtrados na tabela
            for i, item in enumerate(filtered_items, start=1):
                item_button = tk.Button(table_frame, text=item[1], font=("Arial", 14),
                                        command=lambda item=item: show_item_details(item))
                item_button.grid(row=i, column=1, padx=30, pady=10, sticky="w")

                tk.Label(table_frame, text=item[0], font=("Arial", 14)).grid(row=i, column=0, padx=30, pady=10)
                tk.Label(table_frame, text=f"{item[2]:.2f}", font=("Arial", 14)).grid(row=i, column=2, padx=30, pady=10)

        # Função para mostrar detalhes do item selecionado
        def show_item_details(item):
            details_window = tk.Toplevel(stock_window)
            details_window.title("Detalhes do Item")

            # Definindo as dimensões e posição da janela de detalhes
            width_details = int(screen_width * 0.4)
            height_details = int(screen_height * 0.4)
            x_position_details = int((screen_width - width_details) / 2)
            y_position_details = int((screen_height - height_details) / 2)
            details_window.geometry(f"{width_details}x{height_details}+{x_position_details}+{y_position_details}")
            details_window.minsize(width_details, height_details)

            # Variáveis para os campos
            nome_var = tk.StringVar(value=item[1])
            valor_var = tk.StringVar(value=str(item[2]).replace('.', ','))

            # Validação para campos numéricos
            validate_cmd = details_window.register(validate_number_input)

            # Exibição do Código
            tk.Label(details_window, text=f"Código: {item[0]}", font=("Arial", 16)).pack(pady=10)

            # Campo Nome
            tk.Label(details_window, text="Nome:", font=("Arial", 14)).pack(pady=5)
            tk.Entry(details_window, textvariable=nome_var, font=("Arial", 14)).pack(pady=5)

            # Campo Valor com validação
            tk.Label(details_window, text="Valor:", font=("Arial", 14)).pack(pady=5)
            tk.Entry(details_window, textvariable=valor_var, font=("Arial", 14), validate="key", validatecommand=(validate_cmd, '%P')).pack(pady=5)

            # Função para salvar as mudanças
            def save_changes():
                conn = conectar_banco()  # Conectar ao banco
                if conn is None:
                    return  # Se a conexão falhar, saia da função

                cursor = conn.cursor()
                try:
                    new_nome = nome_var.get()
                    new_valor = valor_var.get().replace(',', '.')  # Substituir "," por "." para gravação no banco
                    codigo = item[0]

                    cursor.execute(""" 
                        UPDATE estoque 
                        SET nome = %s, valor = %s 
                        WHERE codigo = %s 
                    """, (new_nome, new_valor, codigo))
                    conn.commit()

                except mysql.connector.Error as err:
                    messagebox.showerror("Erro ao Atualizar", f"Erro ao atualizar o item: {err}")

                finally:
                    cursor.close()  # Feche o cursor
                    conn.close()    # Feche a conexão

                details_window.destroy()
                show_stock_window(stock_window)

            # Função para excluir o item
            def delete_item():
                conn = conectar_banco()  # Conectar ao banco
                if conn is None:
                    return  # Se a conexão falhar, saia da função

                cursor = conn.cursor()
                try:
                    codigo = item[0]
                    cursor.execute("DELETE FROM estoque WHERE codigo = %s", (codigo,))
                    conn.commit()

                except mysql.connector.Error as err:
                    messagebox.showerror("Erro ao Excluir", f"Erro ao excluir o item: {err}")

                finally:
                    cursor.close()  # Feche o cursor
                    conn.close()    # Feche a conexão

                details_window.destroy()
                show_stock_window(stock_window)

            # Botões para Salvar e Excluir
            tk.Button(details_window, text="Salvar", command=save_changes, font=("Arial", 14)).pack(pady=20)
            tk.Button(details_window, text="Excluir", command=delete_item, font=("Arial", 14), fg="red").pack(pady=20)


         # Função para adicionar um novo item
        def save_new_item():
            nome = nome_var.get()
            valor = valor_var.get().replace(',', '.')  # Trocar "," por "." se necessário
            quantidade = quantidade_var.get()
            descricao = descricao_text.get("1.0", tk.END).strip()

            if nome and valor and quantidade:
                try:
                    # Verificar se quantidade é um número inteiro e valor é um número decimal
                    if not quantidade.isdigit():
                        messagebox.showwarning("Entrada inválida", "A quantidade deve ser um número inteiro.")
                        return

                    # Chamar a função de conexão ao banco de dados
                    conn = conectar_banco()
                    if conn is None:
                        return  # Se a conexão falhar, retornar

                    cursor = conn.cursor()

                    # Encontrar o código mais baixo disponível
                    cursor.execute("""
                        SELECT t1.codigo + 1 AS next_codigo
                        FROM estoque t1
                        LEFT JOIN estoque t2 ON t1.codigo + 1 = t2.codigo
                        WHERE t2.codigo IS NULL
                        ORDER BY t1.codigo
                        LIMIT 1
                    """)
                    result = cursor.fetchone()
                    next_codigo = result[0] if result else 1  # Se não encontrar, define como 1

                    # Obter data e hora atual
                    data_entrada = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    # Inserir o novo item na tabela
                    insert_query = """
                    INSERT INTO estoque (codigo, descricao, quantidade, valor, data_entrada, nome)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (next_codigo, descricao, quantidade, valor, data_entrada, nome))

                    # Commit e fechar a conexão
                    conn.commit()
                    cursor.close()
                    conn.close()

                    # Fechar as janelas e atualizar a listagem
                    add_window.destroy()  # Fechar a janela de adicionar item
                    show_stock_window()  # Reabrir a janela de estoque atualizada

                except mysql.connector.Error as err:
                    messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {err}")
                except Exception as e:
                    messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
            else:
                messagebox.showwarning("Entrada inválida", "Por favor, preencha todos os campos obrigatórios.")
                # Janela de adição de itens
        def add_item_window():
            global nome_var, valor_var, quantidade_var, descricao_text, add_window

            add_window = tk.Toplevel(stock_window)
            add_window.title("Adicionar Item")

            # Variáveis
            nome_var = tk.StringVar()
            valor_var = tk.StringVar()
            quantidade_var = tk.StringVar()

            # Validação da entrada numérica
            validate_cmd = add_window.register(validate_number_input)

            # Campo Nome
            tk.Label(add_window, text="Nome:", font=("Arial", 14)).pack()
            tk.Entry(add_window, textvariable=nome_var, font=("Arial", 14)).pack(pady=5)

            # Campo Valor
            tk.Label(add_window, text="Valor:", font=("Arial", 14)).pack()
            valor_entry = tk.Entry(add_window, textvariable=valor_var, font=("Arial", 14), validate="key", validatecommand=(validate_cmd, '%P'))
            valor_entry.pack(pady=5)

            # Campo Quantidade
            tk.Label(add_window, text="Quantidade:", font=("Arial", 14)).pack()
            quantidade_entry = tk.Entry(add_window, textvariable=quantidade_var, font=("Arial", 14), validate="key", validatecommand=(validate_cmd, '%P'))
            quantidade_entry.pack(pady=5)

            # Campo Descrição
            tk.Label(add_window, text="Descrição:", font=("Arial", 14)).pack()
            descricao_text = tk.Text(add_window, height=5, font=("Arial", 14))
            descricao_text.pack(pady=5)

            # Botão para salvar o item
            save_button = tk.Button(add_window, text="Salvar", command=save_new_item, font=("Arial", 14))
            save_button.pack(pady=20)
        # Frame para a barra de busca
        search_frame = tk.Frame(stock_window)
        search_frame.pack(pady=10, padx=10, fill=tk.X)

        # Caixa de entrada para busca e botão de buscar
        search_entry = tk.Entry(search_frame, font=("Arial", 20), width=50)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_button = tk.Button(search_frame, text="Buscar", command=search_items, font=("Arial", 20))
        search_button.pack(side=tk.LEFT)

        # Botão Adicionar
        add_button = tk.Button(search_frame, text="Adicionar", command=add_item_window, font=("Arial", 20))
        add_button.pack(side=tk.LEFT, padx=(40, 0))  # 40 px de espaçamento à esquerda

        # Canvas para a área rolável
        canvas = tk.Canvas(stock_window)
        scrollbar = tk.Scrollbar(stock_window, orient="vertical", command=canvas.yview, width=20)
        scrollable_frame = tk.Frame(canvas)

        # Adicionando o frame ao canvas
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Adicionando o canvas e scrollbar à janela
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Posicionando o canvas e a scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def scroll(event):
            canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

        stock_window.bind("<MouseWheel>", scroll)

        table_frame = tk.Frame(scrollable_frame)
        table_frame.pack(padx=10, pady=10)

        # Exibe todos os itens inicialmente
        update_item_list(items)

    except mysql.connector.Error as err:
        messagebox.showerror("Erro de Consulta", f"Erro ao executar a consulta: {err}")
    finally:
        cursor.close()
        conn.close()
#-----Função para definir o tamanho mínimo da janela ao redimensionar-----#
def on_resize(event):
    min_width = int(screen_width * 0.8)
    min_height = int(screen_height * 0.8)
    root.minsize(min_width, min_height)

# Função para buscar um item no banco de dados pelo código
def buscar_item_no_estoque(codigo):
    conn = conectar_banco()
    if conn is None:
        return None

    cursor = conn.cursor()
    query = "SELECT nome FROM estoque WHERE codigo = %s"
    cursor.execute(query, (codigo,))
    resultado = cursor.fetchone()
    
    cursor.close()
    conn.close()

    return resultado[0] if resultado else None


# -----Função para abrir a janela de venda----- #
# Função para adicionar um item à tabela itens_venda
def adicionar_item_venda(venda_id, codigo_item, quantidade, valor_unitario):
    conn = conectar_banco()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO itens_venda (venda_id, codigo_item, quantidade, valor_unitario) VALUES (%s, %s, %s, %s)",
            (venda_id, codigo_item, quantidade, valor_unitario)
        )
        conn.commit()
        return True
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao adicionar item à venda: {err}")
        return False
    finally:
        conn.close()

#Função para abrir a janela de pagamento e exibir o valor total da venda.
def pagar(id_venda, janela_venda):
    # Estabelecer conexão com o banco
    conn = conectar_banco()
    if conn is None:
        return  # Se não conseguir conectar, sair da função

    cursor = conn.cursor()

    try:
        # Buscar o valor total da venda pelo id_venda fornecido
        cursor.execute("SELECT valor_total FROM vendas WHERE id = %s", (id_venda,))
        venda = cursor.fetchone()

        if venda:
            valor_total = venda[0]
        else:
            messagebox.showerror("Erro", "Venda não encontrada.")
            return  # Se não encontrar a venda, sair da função

    except mysql.connector.Error as err:
        messagebox.showerror("Erro no Banco de Dados", f"Ocorreu um erro: {err}")
        return
    finally:
        cursor.close()
        conn.close()

    # Criar a nova janela de pagamento
    janela_pagar = tk.Toplevel(root)
    janela_pagar.title("Pagamento")

    # Definir tamanho da nova janela
    largura = 400
    altura = 400
    janela_pagar.geometry(f"{largura}x{altura}")

    # Exibir o valor total da venda na janela
    label_valor_venda = tk.Label(janela_pagar, text=f"Valor Total da Venda: R$ {valor_total:.2f}", font=("Arial", 14))
    label_valor_venda.pack(pady=10)

    # Checkbox para selecionar formas de pagamento
    formas_pagamento = {"Dinheiro": tk.IntVar(), "PIX": tk.IntVar(), "Crédito": tk.IntVar(), "Débito": tk.IntVar()}

    for forma, var in formas_pagamento.items():
        tk.Checkbutton(janela_pagar, text=forma, variable=var, font=("Arial", 12)).pack(anchor=tk.W, padx=20)

    def atualizar_interface():
        # Limpa as vendas abertas da interface
        for widget in caixas_frame.winfo_children():
            widget.destroy()  # Remove os widgets antigos

        # Chama a função para carregar as vendas abertas novamente
        carregar_vendas_abertas()


    def confirmar_pagamento():
        selecionados = [forma for forma, var in formas_pagamento.items() if var.get() == 1]

        if len(selecionados) == 0:
            messagebox.showerror("Erro", "Por favor, selecione pelo menos uma forma de pagamento.")
            return

        # Convertendo valor_total para Decimal para manter a precisão e evitar o erro
        valor_total_decimal = Decimal(valor_total)

        # Se houver mais de uma forma de pagamento, pedir a divisão dos valores
        if len(selecionados) > 1:
            total_aplicado = Decimal('0')
            valores_pagamento = {}

            for forma in selecionados:
                while True:
                    valor_str = simpledialog.askstring("Divisão de Pagamento", f"Quanto será pago com {forma}?")
                    
                    # Validar entrada do valor usando a função validate_number_input
                    if validate_number_input(valor_str):
                        valor = Decimal(valor_str.replace(',', '.'))  # Substituir vírgula por ponto e converter para Decimal
                        if valor <= 0 or valor > valor_total_decimal - total_aplicado:
                            messagebox.showerror("Erro", "Valor inválido. Tente novamente.")
                        else:
                            break
                    else:
                        messagebox.showerror("Erro", "Por favor, insira um valor numérico válido.")
                
                total_aplicado += valor
                valores_pagamento[forma] = valor

            # Verificar se o total dos valores bate com o valor total da venda
            if total_aplicado != valor_total_decimal:
                messagebox.showerror("Erro", "Os valores inseridos não correspondem ao total da venda.")
                return

            forma_pagamento_final = "/".join([f"{forma} (R$ {valores_pagamento[forma]:.2f})" for forma in selecionados])
        else:
            # Se for apenas uma forma de pagamento, aplicar o valor total diretamente
            forma_pagamento_final = selecionados[0]
            valores_pagamento = {forma_pagamento_final: valor_total_decimal}  # Aplica o valor total para a forma escolhida

        # Atualizar o banco de dados com as formas de pagamento e o status da venda
        try:
            conn = conectar_banco()
            cursor = conn.cursor()

            # Atualizar a tabela 'vendas'
            cursor.execute("""
                UPDATE vendas 
                SET forma_pagamento = %s, venda_aberta = 'nao' 
                WHERE id = %s
            """, (forma_pagamento_final, id_venda))

            # Atualizar a tabela 'caixa_dia', somando os valores no caixa onde o status é 'aberto'
            cursor.execute("SELECT total_vendas, total_dinheiro, total_pix, total_credito, total_debito FROM caixa_dia WHERE status = 'aberto'")
            caixa = cursor.fetchone()

            if caixa:
                total_vendas_atual, total_dinheiro_atual, total_pix_atual, total_credito_atual, total_debito_atual = map(Decimal, caixa)

                # Somar os valores para cada forma de pagamento
                novo_total_dinheiro = total_dinheiro_atual + valores_pagamento.get('Dinheiro', Decimal('0'))
                novo_total_pix = total_pix_atual + valores_pagamento.get('PIX', Decimal('0'))
                novo_total_credito = total_credito_atual + valores_pagamento.get('Crédito', Decimal('0'))
                novo_total_debito = total_debito_atual + valores_pagamento.get('Débito', Decimal('0'))

                # Atualizar o saldo total das vendas
                novo_total_vendas = total_vendas_atual + valor_total_decimal

                cursor.execute("""
                    UPDATE caixa_dia
                    SET total_vendas = %s, total_dinheiro = %s, total_pix = %s, total_credito = %s, total_debito = %s
                    WHERE status = 'aberto'
                """, (novo_total_vendas, novo_total_dinheiro, novo_total_pix, novo_total_credito, novo_total_debito))

            conn.commit()
            messagebox.showinfo("Sucesso", "Pagamento registrado com sucesso!")

        except mysql.connector.Error as err:
            messagebox.showerror("Erro no Banco de Dados", f"Ocorreu um erro: {err}")
        finally:
            cursor.close()
            conn.close()
        
        # Atualizar a interface
        atualizar_interface()  # Chama a nova função para atualizar a tela

        janela_pagar.destroy()
        janela_venda.destroy()



    # Botão para confirmar o pagamento
    botao_confirmar = tk.Button(janela_pagar, text="Confirmar Pagamento", font=("Arial", 12), command=confirmar_pagamento)
    botao_confirmar.pack(pady=20)

    # Botão para fechar a janela
    botao_fechar = tk.Button(janela_pagar, text="Cancelar", font=("Arial", 12), command=janela_pagar.destroy)
    botao_fechar.pack(pady=10)

def abrir_janela_editar(venda_id, nome_caixa):
    # Verificar se a janela principal (root) está acessível
    if 'root' not in globals():
        messagebox.showerror("Erro", "Janela principal não encontrada.")
        return
    
    # Conectar ao banco de dados para buscar o nome da venda
    conn = conectar_banco()
    if conn is None:
        return  # Se a conexão falhar, a função será encerrada

    cursor = conn.cursor()

    try:
        # Consulta para buscar o nome da venda baseado no venda_id
        query_nome_venda = "SELECT nome FROM vendas WHERE id = %s"
        cursor.execute(query_nome_venda, (venda_id,))
        resultado = cursor.fetchone()

        if resultado:
            nome_venda = resultado[0]  # Pegar o nome da venda
        else:
            nome_venda = f"Venda {venda_id}"  # Caso não encontre o nome, usar o ID como fallback

    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao buscar o nome da venda: {err}")
        return
    finally:
        cursor.close()
        conn.close()

    # Criar a nova janela
    janela_editar = tk.Toplevel(root)
    janela_editar.title(f"Editar Venda - {nome_venda}")

    # Definir tamanho inicial
    largura_inicial = 700
    altura_inicial = 600
    janela_editar.geometry(f"{largura_inicial}x{altura_inicial}")

    # Permitir redimensionar a janela
    janela_editar.minsize(largura_inicial, altura_inicial)

    # Label informativa com o nome da venda
    label_info = tk.Label(janela_editar, text=f"Editando venda: {nome_venda}", font=("Arial", 14))
    label_info.pack(pady=10)

    # Frame para listar os itens da venda
    lista_itens_frame = tk.Frame(janela_editar)
    lista_itens_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    # Conectar novamente ao banco de dados para buscar os itens da venda
    conn = conectar_banco()
    if conn is None:
        return  # Se a conexão falhar, a função será encerrada

    cursor = conn.cursor()

    try:
        # Consulta para buscar os itens da venda
        query_itens = """
            SELECT i.id, i.quantidade, e.nome, e.valor 
            FROM itens_venda i
            JOIN estoque e ON i.codigo_item = e.codigo 
            WHERE i.venda_id = %s
        """
        cursor.execute(query_itens, (venda_id,))
        itens = cursor.fetchall()

        def atualizar_valor_total():
            """Atualiza o valor total da venda com base nos itens."""
            try:
                conn_atualizar_valor = conectar_banco()
                cursor_valor = conn_atualizar_valor.cursor()

                # Consulta para calcular o valor total com base nos itens restantes
                query_valor_total = """
                    SELECT SUM(i.quantidade * e.valor) 
                    FROM itens_venda i
                    JOIN estoque e ON i.codigo_item = e.codigo 
                    WHERE i.venda_id = %s
                """
                cursor_valor.execute(query_valor_total, (venda_id,))
                novo_valor_total = cursor_valor.fetchone()[0] or 0.0

                # Atualizar o valor total na tabela 'vendas'
                query_atualizar_venda = "UPDATE vendas SET valor_total = %s WHERE id = %s"
                cursor_valor.execute(query_atualizar_venda, (novo_valor_total, venda_id))

                conn_atualizar_valor.commit()
                cursor_valor.close()
                conn_atualizar_valor.close()

            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao atualizar o valor total: {err}")

        def atualizar_quantidade(item_id, nova_quantidade):
            """Função para atualizar a quantidade de um item no banco de dados."""
            try:
                conn_atualizar = conectar_banco()
                cursor_atualizar = conn_atualizar.cursor()
                query_atualizar = "UPDATE itens_venda SET quantidade = %s WHERE id = %s"
                cursor_atualizar.execute(query_atualizar, (nova_quantidade, item_id))
                conn_atualizar.commit()
                cursor_atualizar.close()
                conn_atualizar.close()
                atualizar_valor_total()  # Atualizar o valor total da venda

            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao atualizar a quantidade: {err}")

        def deletar_item(item_id):
            """Função para deletar um item da venda no banco de dados."""
            try:
                conn_deletar = conectar_banco()
                cursor_deletar = conn_deletar.cursor()
                query_deletar = "DELETE FROM itens_venda WHERE id = %s"
                cursor_deletar.execute(query_deletar, (item_id,))
                conn_deletar.commit()
                cursor_deletar.close()
                conn_deletar.close()
                atualizar_valor_total()  # Atualizar o valor total da venda

                # Recarregar a janela de edição para atualizar a lista de itens
                janela_editar.destroy()
                reabrir()

            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao deletar o item: {err}")

        # Exibir os itens no frame
        for item_id, quantidade, nome_item, valor_item in itens:
            # Criar um Frame para alinhar os labels
            item_frame = tk.Frame(lista_itens_frame)
            item_frame.pack(fill=tk.X, pady=5)

            # Label para o nome do item
            item_label = tk.Label(item_frame, text=f"{nome_item} - R${valor_item:.2f} cada", font=("Arial", 14), anchor="w")
            item_label.pack(side=tk.LEFT, padx=(10, 10))

            # Entry para a quantidade
            quantidade_entry = tk.Entry(item_frame, font=("Arial", 14), width=5)
            quantidade_entry.insert(0, str(quantidade))  # Colocar a quantidade atual
            quantidade_entry.pack(side=tk.LEFT, padx=(10, 10))

            # Botão para atualizar a quantidade
            botao_atualizar = tk.Button(item_frame, text="Atualizar", font=("Arial", 12),
                                        command=lambda id=item_id, entry=quantidade_entry: atualizar_quantidade(id, entry.get()))
            botao_atualizar.pack(side=tk.LEFT, padx=(10, 10))

            # Botão para deletar o item
            botao_deletar = tk.Button(item_frame, text="Deletar", font=("Arial", 12),
                                      command=lambda id=item_id: deletar_item(id))
            botao_deletar.pack(side=tk.LEFT, padx=(10, 10))

    except mysql.connector.Error as err:
        messagebox.showerror("Erro ao carregar itens", f"Erro ao consultar itens da venda: {err}")

    finally:
        cursor.close()
        conn.close()

    # Botão para fechar a janela de edição e reabrir a janela de venda
    def reabrir():
        janela_editar.destroy()  # Fecha a janela de edição
        abrir_janela_venda(nome_caixa)  # Reabre a janela de venda

    botao_fechar = tk.Button(janela_editar, text="Fechar", font=("Arial", 14), command=reabrir)
    botao_fechar.pack(pady=20)

def abrir_janela_venda(nome_caixa):
    janela_venda = tk.Toplevel(root)
    janela_venda.title(f"Visualizar Venda - {nome_caixa if nome_caixa else 'Não informado'}")

    # Definir tamanho inicial
    largura_inicial = 700
    altura_inicial = 600
    janela_venda.geometry(f"{largura_inicial}x{altura_inicial}")

    # Permitir redimensionar a janela
    janela_venda.minsize(largura_inicial, altura_inicial)
    janela_venda.maxsize(width=None, height=None)

    label_info = tk.Label(janela_venda, text=f"{nome_caixa if nome_caixa else 'Não informado'}", font=("Arial", 14))
    label_info.pack(pady=10)

    # Frame para a barra de busca e a quantidade
    search_frame = tk.Frame(janela_venda)
    search_frame.pack(pady=10)

    # Barra de busca (Entry)
    barra_busca = tk.Entry(search_frame, font=("Arial", 12), width=30)
    barra_busca.pack(side=tk.LEFT, padx=10)

    # Campo para quantidade
    label_quantidade = tk.Label(search_frame, text="Quantidade:", font=("Arial", 12))
    label_quantidade.pack(side=tk.LEFT, padx=5)
    entrada_quantidade = tk.Entry(search_frame, font=("Arial", 12), width=5)
    entrada_quantidade.pack(side=tk.LEFT, padx=5)
    entrada_quantidade.insert(0, "1")

    # Label para mostrar o resultado da busca
    resultado_label = tk.Label(janela_venda, text="", font=("Arial", 12))
    resultado_label.pack(pady=10)

    # Frame para mostrar a lista de itens adicionados
    lista_itens_frame = tk.Frame(janela_venda)
    lista_itens_frame.pack(pady=10)

    # Label para mostrar o valor total
    valor_total_label = tk.Label(janela_venda, text="Valor total: R$ 0.00", font=("Arial", 22))
    valor_total_label.pack(pady=10)

    # Adicionando botões na parte inferior da janela
    botoes_frame = tk.Frame(janela_venda)
    botoes_frame.pack(pady=20, side=tk.BOTTOM)

    # Botão "Pagar" com ícone de dinheiro
    botao_pagar = tk.Button(botoes_frame, text="Pagar", font=("Arial", 14), command=lambda: pagar(venda_id,janela_venda))
    botao_pagar.pack(side=tk.LEFT, padx=10)
    # Botão "Editar"
    botao_editar = tk.Button(
        botoes_frame, 
        text="Editar", 
        font=("Arial", 14), 
        command=lambda: (janela_venda.destroy(), abrir_janela_editar(venda_id, nome_caixa))
    )
    botao_editar.pack(side=tk.LEFT, padx=10)


    # Conectar ao banco de dados
    conn = conectar_banco()
    if conn is None:
        return  # Se a conexão falhar, a função será encerrada

    cursor = conn.cursor()

    try:
        # Consulta para buscar o valor_total da venda com o nome especificado e verificar se a venda está aberta
        query = "SELECT id, valor_total FROM vendas WHERE nome = %s AND venda_aberta = 'sim'"
        cursor.execute(query, (nome_caixa,))
        resultado = cursor.fetchone()

        if resultado:
            venda_id, valor_total = resultado  # Pegar o id e o valor total da tupla retornada
            valor_total_label.config(text=f"Valor total: R$ {valor_total:.2f}")  # Atualizar o texto da label

            # Consulta para buscar os itens da venda, incluindo o nome do item
            query_itens = """
                SELECT i.quantidade, e.nome, i.valor_unitario 
                FROM itens_venda i
                JOIN estoque e ON i.codigo_item = e.codigo 
                WHERE i.venda_id = %s
            """
            cursor.execute(query_itens, (venda_id,))
            itens = cursor.fetchall()

            # Exibir os itens no frame
            for quantidade, nome_item, valor_unitario in itens:
                valor_total_item = quantidade * valor_unitario  # Calcular o valor total para aquele item
                
                # Criar um Frame para alinhar os labels
                item_frame = tk.Frame(lista_itens_frame)
                item_frame.pack(fill=tk.X)  # Preencher horizontalmente

                # Label para a quantidade e o nome do item
                item_label = tk.Label(item_frame, text=f"{quantidade} {nome_item}", font=("Arial", 18), anchor="w")
                item_label.pack(side=tk.LEFT, padx=(0, 10))  # Alinhado à esquerda com margem à direita

                # Label para o valor total, alinhado à direita
                valor_label = tk.Label(item_frame, text=f"R$ {valor_total_item:.2f}", font=("Arial", 18), anchor="e")
                valor_label.pack(side=tk.RIGHT)  # Alinhado à direita

        else:
            valor_total_label.config(text="Valor total: R$ 0.00")  # Caso não encontre a venda ou a venda não esteja aberta

    except mysql.connector.Error as err:
        messagebox.showerror("Erro ao carregar venda", f"Erro ao consultar valor total: {err}")

    finally:
        # Fechar a conexão com o banco de dados
        cursor.close()
        conn.close()


    # Função para atualizar a lista de itens e o valor total
    def atualizar_lista():
        nonlocal venda_id  # Permite modificar a variável venda_id
        conn = conectar_banco()
        if conn is None:
            return  # Se a conexão falhar, a função será encerrada

        cursor = conn.cursor()

        try:
            # Consulta para buscar os itens da venda, incluindo o nome do item
            query_itens = """
                SELECT i.quantidade, e.nome, i.valor_unitario 
                FROM itens_venda i
                JOIN estoque e ON i.codigo_item = e.codigo 
                WHERE i.venda_id = %s
            """
            cursor.execute(query_itens, (venda_id,))
            itens = cursor.fetchall()

            # Limpar a lista de itens antes de adicionar os novos
            for widget in lista_itens_frame.winfo_children():
                widget.destroy()

            # Exibir os itens no frame
            for quantidade, nome_item, valor_unitario in itens:
                valor_total_item = quantidade * valor_unitario  # Calcular o valor total para aquele item
                
                # Criar um Frame para alinhar os labels
                item_frame = tk.Frame(lista_itens_frame)
                item_frame.pack(fill=tk.X)  # Preencher horizontalmente

                # Label para a quantidade e o nome do item
                item_label = tk.Label(item_frame, text=f"{quantidade} {nome_item}", font=("Arial", 18), anchor="w")
                item_label.pack(side=tk.LEFT, padx=(0, 10))  # Alinhado à esquerda com margem à direita

                # Label para o valor total, alinhado à direita
                valor_label = tk.Label(item_frame, text=f"R$ {valor_total_item:.2f}", font=("Arial", 18), anchor="e")
                valor_label.pack(side=tk.RIGHT)  # Alinhado à direita

            # Atualizar o valor total
            query_valor_total = "SELECT valor_total FROM vendas WHERE id = %s"
            cursor.execute(query_valor_total, (venda_id,))
            novo_valor_total = cursor.fetchone()
            if novo_valor_total:
                valor_total_label.config(text=f"Valor total: R$ {novo_valor_total[0]:.2f}")

        except mysql.connector.Error as err:
            messagebox.showerror("Erro ao carregar itens", f"Erro ao consultar itens da venda: {err}")

        finally:
            # Fechar a conexão com o banco de dados
            cursor.close()
            conn.close()

    # Botão para adicionar o item
    adicionar_item_button = tk.Button(
        search_frame,
        text="Adicionar",
        font=("Arial", 12),
        state=tk.NORMAL,  # Habilitar o botão se quiser permitir que o usuário clique
        command=lambda: [
            adicionar_item(barra_busca.get(), entrada_quantidade.get(), barra_busca, entrada_quantidade),
            atualizar_lista()  # Atualiza a lista de itens e o valor total após adicionar
        ]
    )
    adicionar_item_button.pack(side=tk.LEFT, padx=5)

    # Atualizar a lista inicialmente ao abrir a janela
    atualizar_lista()

    # Função para buscar o item no banco de dados e exibir o nome
    def buscar_item(codigo_str):
            if codigo_str.isdigit():
                codigo = int(codigo_str)
                item = buscar_item_no_estoque(codigo)
                if item:
                    nome_item, valor_total= item
                    resultado_label.config(text=f"Item encontrado: {nome_item}")
                    adicionar_item_button.config(state=tk.NORMAL)
                else:
                    resultado_label.config(text="Código inválido")
                    adicionar_item_button.config(state=tk.DISABLED)
            else:
                resultado_label.config(text="")
                adicionar_item_button.config(state=tk.DISABLED)

    # Adicionar evento para fazer a busca enquanto o usuário digita
    barra_busca.bind("<KeyRelease>", lambda event: buscar_item(barra_busca.get()))

    # Função para adicionar o item na lista de compras e banco de dados
    def adicionar_item(codigo_str, quantidade_str, campo_codigo, campo_quantidade):
        nonlocal valor_total  # Permitir atualizar a variável valor_total
        if not codigo_str.isdigit() or not quantidade_str.isdigit():
            messagebox.showwarning("Erro", "Código ou quantidade inválidos.")
            return

        codigo = int(codigo_str)
        quantidade = int(quantidade_str)
        item = buscar_item_no_estoque(codigo)  # Função que retorna o item do estoque
        if item:
            nome_item, valor_unitario = item
            valor_item_total = valor_unitario * quantidade

            # Conectar ao banco de dados
            conn = conectar_banco()
            if conn is None:
                messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.")
                return

            cursor = conn.cursor()

            try:
                # 1. Buscar o valor total atual da venda
                query = "SELECT valor_total FROM vendas WHERE id = %s"  # Ajuste o ID conforme necessário
                cursor.execute(query, (venda_id,))  # Certifique-se de que 'venda_id' está definido corretamente
                resultado = cursor.fetchone()

                if resultado:
                    valor_total_atual = resultado[0]
                    novo_valor_total = valor_total_atual + valor_item_total

                    # 2. Atualizar o valor total na tabela de vendas
                    update_query = "UPDATE vendas SET valor_total = %s WHERE id = %s"
                    cursor.execute(update_query, (novo_valor_total, venda_id))
                    conn.commit()

                    # Chamar a função para registrar o item vendido em uma tabela separada
                    sucesso = adicionar_item_venda(venda_id, codigo, quantidade, valor_unitario)
                    if sucesso: 
                        # Limpar os campos após a adição
                        campo_codigo.delete(0, tk.END)  # Limpa o campo de código
                        campo_quantidade.delete(0, tk.END)  # Limpa o campo de quantidade

                else:
                    messagebox.showwarning("Erro", "Venda não encontrada.")

            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao atualizar venda: {err}")

            finally:
                cursor.close()
                conn.close()
        else:
            messagebox.showwarning("Erro", "O item não foi encontrado no estoque.")


            conn.close()


    # Função para adicionar a venda ao banco de dados
    def adicionar_item_venda(venda_id, codigo_item, quantidade, valor_unitario):
        conn = conectar_banco()
        if conn is None:
            return False  # Retorna False se a conexão falhar

        cursor = conn.cursor()
        
        try:
            # Insira o item vendido na tabela de itens
            query = """
                INSERT INTO itens_venda (venda_id, codigo_item, quantidade, valor_unitario)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (venda_id, codigo_item, quantidade, valor_unitario))
            conn.commit()  # Confirmar a transação
            return True  # Retorna True se a inserção for bem-sucedida

        except mysql.connector.Error as err:
            messagebox.showerror("Erro ao adicionar item", f"Erro ao inserir dados da venda: {err}")
            return False  # Retorna False em caso de erro

        finally:
            cursor.close()
            conn.close()


# Exemplo de como buscar um item no estoque (isso depende da sua estrutura de banco de dados)
def buscar_item_no_estoque(codigo):
    conn = conectar_banco()
    if conn is None:
        return None

    cursor = conn.cursor()

    try:
        # Supondo que a tabela estoque tenha os campos codigo, nome e valor
        query = "SELECT nome, valor FROM estoque WHERE codigo = %s"
        cursor.execute(query, (codigo,))
        result = cursor.fetchone()
        return result if result else None

    except mysql.connector.Error as err:
        messagebox.showerror("Erro ao buscar item", f"Erro ao consultar item no estoque: {err}")
        return None

    finally:
        cursor.close()
        conn.close()

#-----Função para criar uma nova "caixa de venda"-----#
def criar_nova_venda():
    # Pergunta ao usuário se ele deseja nomear a caixa
    nome_caixa = simpledialog.askstring("Nome da Venda", "Digite um nome para a nova venda (ou deixe em branco):")

    # Garantir que 'nome_caixa' não seja None ou vazio
    if not nome_caixa:
        nome_caixa = "Venda Anônima"

    # Limitar o tamanho do nome da caixa a 10 caracteres, abreviando com "..."
    max_nome_len = 10
    nome_caixa_abreviado = nome_caixa if len(nome_caixa) <= max_nome_len else nome_caixa[:max_nome_len] + "..."

    # Conectar ao banco de dados
    conn = conectar_banco()
    if conn is None:
        return  # Se a conexão falhar, a função para aqui

    cursor = conn.cursor()

    try:
        # Inserir a nova venda na tabela 'vendas'
        query_venda = """
            INSERT INTO vendas (nome, forma_pagamento, valor_total, data_venda, venda_aberta)
            VALUES (%s, %s, %s, NOW(), %s)
        """
        cursor.execute(query_venda, (nome_caixa, None, 0.00, 'sim'))
        conn.commit()

    except mysql.connector.Error as err:
        messagebox.showerror("Erro ao Inserir", f"Erro ao inserir nova venda: {err}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

    # Criar uma nova Frame que será a caixa de venda
    caixa_frame = tk.Frame(caixas_frame, bg="lightgray", width=150, height=150, bd=2, relief=tk.RAISED)
    caixa_frame.grid_propagate(False)  # Evitar que o tamanho da frame se ajuste automaticamente
    caixa_frame.pack_propagate(False)  # Evitar que o conteúdo interno ajuste o tamanho da caixa

    # Botão na caixa de venda para abrir a janela de visualização
    caixa_button = tk.Button(caixa_frame, text=nome_caixa_abreviado, font=("Arial", 12), wraplength=140,
                             command=lambda: abrir_janela_venda(nome_caixa), bg="white", relief=tk.FLAT)
    caixa_button.pack(expand=True, fill=tk.BOTH)

    # Posicionar as caixas em um grid de 15 por linha
    total_caixas = len(caixas_frame.grid_slaves())  # Contar quantas caixas já foram criadas
    linha = total_caixas // 15  # Determinar em qual linha a caixa será colocada
    coluna = total_caixas % 15  # Determinar em qual coluna da linha a caixa será colocada

    # Adicionar o frame (caixa) na janela principal
    caixa_frame.grid(row=linha, column=coluna, padx=20, pady=10)

    # Abrir automaticamente a janela da nova venda após sua criação
    abrir_janela_venda(nome_caixa)

def carregar_vendas_abertas():
    # Conectar ao banco de dados
    conn = conectar_banco()
    if conn is None:
        return  # Se a conexão falhar, a função será encerrada

    cursor = conn.cursor()

    try:
        # Consulta para buscar vendas com 'venda_aberta' = 'sim'
        query = "SELECT id, nome FROM vendas WHERE venda_aberta = 'sim'"
        cursor.execute(query)

        # Obter os resultados da consulta
        vendas_abertas = cursor.fetchall()

        for venda in vendas_abertas:
            id_venda, nome_caixa = venda

            # Limitar o tamanho do nome da caixa a 10 caracteres, abreviando com "..."
            max_nome_len = 10
            nome_caixa_abreviado = nome_caixa if nome_caixa and len(nome_caixa) <= max_nome_len else (nome_caixa[:max_nome_len] + "...") if nome_caixa else "Não informado"

            # Criar uma nova Frame que será a caixa de venda
            caixa_frame = tk.Frame(caixas_frame, bg="lightgray", width=150, height=150, bd=2, relief=tk.RAISED)
            caixa_frame.grid_propagate(False)  # Evitar que o tamanho da frame se ajuste automaticamente
            caixa_frame.pack_propagate(False)  # Evitar que o conteúdo interno ajuste o tamanho da caixa

            # Botão na caixa de venda para abrir a janela de visualização
            caixa_button = tk.Button(caixa_frame, text=nome_caixa_abreviado, font=("Arial", 12), wraplength=140,
                                     command=lambda nome_caixa=nome_caixa: abrir_janela_venda(nome_caixa), bg="white", relief=tk.FLAT)
            caixa_button.pack(expand=True, fill=tk.BOTH)

            # Posicionar as caixas em um grid de 15 por linha
            total_caixas = len(caixas_frame.grid_slaves())  # Contar quantas caixas já foram criadas
            linha = total_caixas // 15  # Determinar em qual linha a caixa será colocada
            coluna = total_caixas % 15  # Determinar em qual coluna da linha a caixa será colocada

            # Adicionar o frame (caixa) na janela principal
            caixa_frame.grid(row=linha, column=coluna, padx=20, pady=10)  # Espaçamento entre as caixas

    except mysql.connector.Error as err:
        messagebox.showerror("Erro ao carregar vendas", f"Erro ao consultar vendas abertas: {err}")

    finally:
        # Fechar a conexão com o banco de dados
        cursor.close()
        conn.close()

# Criando a janela principal
root = tk.Tk()
root.title("Caixa do Dia")

# Obtendo o tamanho da tela do usuário
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Definindo o programa para iniciar em tela cheia sem esconder os botões de controle
root.geometry(f"{screen_width}x{screen_height}")
root.state('zoomed')

# Faixa branca no topo com altura definida
top_bar = tk.Frame(root, bg="white", height=200)
top_bar.pack(side=tk.TOP, fill=tk.X)

# Adicionando ícones (botões) na faixa branca com altura e espaçamento definidos
icon1 = tk.Button(top_bar, text="🖥️ Caixa", command=caixa_status, bg="white", borderwidth=0, font=("Arial", 24), width=15, height=5)
icon1.pack(side=tk.LEFT, padx=(80, 0))

icon2 = tk.Button(top_bar, text="📦 Estoque", command=show_stock_window, bg="white", borderwidth=0, font=("Arial", 24), width=15, height=5)
icon2.pack(side=tk.LEFT, padx=(80, 0))

icon3 = tk.Button(top_bar, text="🛒 Nova Venda", command=criar_nova_venda, bg="white", borderwidth=0, font=("Arial", 24), width=15, height=5)
icon3.pack(side=tk.LEFT, padx=(80, 0))

# Adicionando uma nova seção para organizar as caixas de vendas
caixas_frame = tk.Frame(root)
caixas_frame.pack(side=tk.TOP, pady=20)

# Chame essa função ao iniciar o programa para carregar as vendas já abertas
carregar_vendas_abertas()

# Evento para redimensionar a janela com tamanho mínimo especificado
root.bind("<Configure>", on_resize)

# Iniciando o loop da interface
root.mainloop()

