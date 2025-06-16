import requests
from bs4 import BeautifulSoup
import pdfkit
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os


def download_files(url, save_folder, progress_text, target_heading):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    total_files = 0
    downloaded_files_count = 0  # 関数内でカウントするための変数
    success = True

    exam_data = []

    # 指定された見出しを探す
    target_section = soup.find("h2", class_="wp-block-heading", text=target_heading)

    if target_section:
        table = target_section.find_next("table")
        if table:
            for row in table.find_all("tr"):
                cells = row.find_all("td", style="text-align:center")
                if (
                    len(cells) >= 4
                ):  # 午前問題、午後問題、正答肢表がある行 (はり師きゅう師)
                    exam_info = {}
                    am_anchor = cells[1].find("a", text=lambda t: t and "午前問題" in t)
                    if am_anchor and "href" in am_anchor.attrs:
                        exam_info["am_pdf"] = requests.compat.urljoin(
                            url, am_anchor["href"]
                        )
                    pm_anchor = cells[2].find("a", text=lambda t: t and "午後問題" in t)
                    if pm_anchor and "href" in pm_anchor.attrs:
                        exam_info["pm_pdf"] = requests.compat.urljoin(
                            url, pm_anchor["href"]
                        )
                    ans_anchor = cells[3].find(
                        "a",
                        text=lambda t: t
                        and ("正答" in t or "解答" in t or "正答肢表" in t),
                    )
                    if ans_anchor and "href" in ans_anchor.attrs:
                        exam_info["answer_html"] = requests.compat.urljoin(
                            url, ans_anchor["href"]
                        )
                    if exam_info:
                        exam_data.append(exam_info)
                        total_files += 2  # 午前と午後で2ファイル

                elif (
                    len(cells) >= 3
                ):  # 午前問題、午後問題、正答肢表がある行 (あん摩マッサージ指圧師)
                    exam_info = {}
                    am_anchor = cells[1].find("a", text=lambda t: t and "午前問題" in t)
                    if am_anchor and "href" in am_anchor.attrs:
                        exam_info["am_pdf"] = requests.compat.urljoin(
                            url, am_anchor["href"]
                        )
                    pm_anchor = cells[2].find("a", text=lambda t: t and "午後問題" in t)
                    if pm_anchor and "href" in pm_anchor.attrs:
                        exam_info["pm_pdf"] = requests.compat.urljoin(
                            url, pm_anchor["href"]
                        )
                    ans_anchor_cell = (
                        cells[3] if len(cells) > 3 else cells[2]
                    )  # 正答肢表のセル位置を調整
                    ans_anchor = ans_anchor_cell.find(
                        "a",
                        text=lambda t: t
                        and ("正答" in t or "解答" in t or "正答肢表" in t),
                    )
                    if ans_anchor and "href" in ans_anchor.attrs:
                        exam_info["answer_html"] = requests.compat.urljoin(
                            url, ans_anchor["href"]
                        )
                    if exam_info:
                        exam_data.append(exam_info)
                        total_files += 2  # 午前と午後で2ファイル

            progress_text.config(state=tk.NORMAL)
            progress_text.insert(
                tk.END,
                f"解析中: {target_heading}の問題と解答のリンクを特定しました ({total_files}ファイル)\n",
            )
            progress_text.see(tk.END)
            progress_text.config(state=tk.DISABLED)
            root.update()

            for data in exam_data:
                try:
                    # 午前問題のダウンロード
                    if "am_pdf" in data:
                        pdf_url = data["am_pdf"]
                        pdf_filename_base = pdf_url.split("/")[-1].replace(".pdf", "")
                        pdf_filename = os.path.join(
                            save_folder, f"{pdf_filename_base}.pdf"
                        )
                        progress_text.config(state=tk.NORMAL)
                        progress_text.insert(
                            tk.END, f"ダウンロード中: {pdf_filename}\n"
                        )
                        progress_text.see(tk.END)
                        progress_text.config(state=tk.DISABLED)
                        root.update()
                        pdf_response = requests.get(pdf_url)
                        pdf_response.raise_for_status()
                        with open(pdf_filename, "wb") as f:
                            f.write(pdf_response.content)
                        downloaded_files_count += 1

                    # 午後問題のダウンロード
                    if "pm_pdf" in data:
                        pdf_url = data["pm_pdf"]
                        pdf_filename_base = pdf_url.split("/")[-1].replace(".pdf", "")
                        pdf_filename = os.path.join(
                            save_folder, f"{pdf_filename_base}.pdf"
                        )
                        progress_text.config(state=tk.NORMAL)
                        progress_text.insert(
                            tk.END, f"ダウンロード中: {pdf_filename}\n"
                        )
                        progress_text.see(tk.END)
                        progress_text.config(state=tk.DISABLED)
                        root.update()
                        pdf_response = requests.get(pdf_url)
                        pdf_response.raise_for_status()
                        with open(pdf_filename, "wb") as f:
                            f.write(pdf_response.content)
                        downloaded_files_count += 1

                    # 正答肢表のダウンロードと変換
                    if "answer_html" in data:
                        ans_url = data["answer_html"]
                        ans_filename_base_html = (
                            ans_url.split("/")[-1]
                            .replace(".html", "")
                            .replace(".htm", "")
                        )
                        # 問題PDFのファイル名からベース部分を取得してアンサーPDFのファイル名を作成
                        if "am_pdf" in data:
                            mondai_filename_base = (
                                data["am_pdf"].split("/")[-1].replace(".pdf", "")
                            )
                            ans_pdf_filename = os.path.join(
                                save_folder, f"{mondai_filename_base}_answer.pdf"
                            )
                        elif "pm_pdf" in data:
                            mondai_filename_base = (
                                data["pm_pdf"].split("/")[-1].replace(".pdf", "")
                            )
                            ans_pdf_filename = os.path.join(
                                save_folder, f"{mondai_filename_base}_answer.pdf"
                            )
                        else:
                            ans_pdf_filename = os.path.join(
                                save_folder, f"{ans_filename_base_html}_answer.pdf"
                            )

                        progress_text.config(state=tk.NORMAL)
                        progress_text.insert(
                            tk.END, f"変換中: {ans_url} -> {ans_pdf_filename}\n"
                        )
                        progress_text.see(tk.END)
                        progress_text.config(state=tk.DISABLED)
                        root.update()
                        try:
                            pdfkit.from_url(ans_url, ans_pdf_filename)
                            downloaded_files_count += 1
                        except Exception as e:
                            progress_text.config(state=tk.NORMAL)
                            progress_text.insert(
                                tk.END,
                                f"エラー: 正答肢表のPDF変換に失敗しました - {e}\n",
                            )
                            progress_text.see(tk.END)
                            progress_text.config(state=tk.DISABLED)
                            root.update()
                            success = False

                except requests.exceptions.RequestException as e:
                    progress_text.config(state=tk.NORMAL)
                    progress_text.insert(
                        tk.END, f"エラー: ファイルのダウンロードに失敗しました - {e}\n"
                    )
                    progress_text.see(tk.END)
                    progress_text.config(state=tk.DISABLED)
                    root.update()
                    success = False
                except Exception as e:
                    progress_text.config(state=tk.NORMAL)
                    progress_text.insert(
                        tk.END, f"エラー: ファイルの保存に失敗しました - {e}\n"
                    )
                    progress_text.see(tk.END)
                    progress_text.config(state=tk.DISABLED)
                    root.update()
                    success = False

            return success, downloaded_files_count


def on_fetch():
    url = url_entry.get()
    save_folder = folder_entry.get()
    target_heading = heading_var.get()  # ラジオボタンで選択された見出しを取得

    progress_text = scrolledtext.ScrolledText(root, width=60, height=5)
    progress_text.pack(pady=5)
    progress_text.config(state=tk.DISABLED)

    success, downloaded_count = download_files(
        url, save_folder, progress_text, target_heading
    )

    if success and downloaded_count > 0:
        messagebox.showinfo("完了", "データの取得に成功しました！")
    elif not success:
        messagebox.showerror(
            "エラー",
            "一部またはすべてのデータの取得に失敗しました。詳細は処理状況をご確認ください。",
        )
    else:
        messagebox.showinfo("情報", "該当する問題データが見つかりませんでした。")


# GUIの設定
root = tk.Tk()
root.title("あはき問題正答取得アプリ")

# 説明文
description_label = tk.Label(
    root,
    text="あん摩マッサージ指圧師国家試験問題および正答\nはり師きゅう師国家試験問題および正答をPDFで取得します。\n\n取得先URLに変更があった場合は、適切なURLを入力してください。",
)
description_label.pack(pady=5)

# URL入力欄
url_label = tk.Label(
    root, text="問題・正答取得先URL：\n（東洋療法試験財団の過去の試験問題等）"
)
url_label.pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.insert(0, "https://ahaki.or.jp/exam/archives/")
url_entry.pack(pady=5)

# 保存先入力欄
folder_label = tk.Label(root, text="保存先:")
folder_label.pack(pady=5)
folder_entry = tk.Entry(root, width=50)
folder_entry.insert(0, os.path.expanduser("~/Desktop"))  # デフォルトはデスクトップ
folder_entry.pack(pady=5)


# 保存先フォルダ選択ボタン
def browse_folder():
    folder_path = filedialog.askdirectory()
    folder_entry.delete(0, tk.END)
    folder_entry.insert(0, folder_path)


browse_button = tk.Button(root, text="フォルダ選択", command=browse_folder)
browse_button.pack(pady=5)

# 対象選択ラジオボタン
heading_var = tk.StringVar(
    value="あん摩マッサージ指圧師国家試験問題及び正答肢表　墨字版"
)  # デフォルト値
heading_label = tk.Label(root, text="対象データ:")
heading_label.pack(pady=5)
tk.Radiobutton(
    root,
    text="あん摩マッサージ指圧師",
    variable=heading_var,
    value="あん摩マッサージ指圧師国家試験問題及び正答肢表　墨字版",
).pack()
tk.Radiobutton(
    root,
    text="はり師きゅう師",
    variable=heading_var,
    value="はり師きゅう師国家試験問題及び正答肢表　墨字版",
).pack()


# 取得ボタン
fetch_button = tk.Button(root, text="取得", command=on_fetch)
fetch_button.pack(pady=20)

# アプリケーションの実行
root.mainloop()
