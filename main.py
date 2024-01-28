import json
import os
from urllib import request
import flet as ft
from dotenv import load_dotenv
from webbrowser import open

load_dotenv(".env")


class Suggest:
    def __init__(self, suggest: dict) -> None:
        self.target = suggest["word"]
        self.fix_suggestion = suggest["suggestion"]
        self.rule = suggest["rule"]
        self.note = suggest["note"]
        self.offset = int(suggest["offset"])
        self.length = int(suggest["length"])

    def get_context(self, raw_contents: str):
        word_start = self.offset
        word_end = self.offset + self.length
        context_start = max(word_start - 10, 0)
        context_end = min(word_end + 10, len(raw_contents))
        context = (
            raw_contents[context_start:word_start]
            + "▶"
            + raw_contents[word_start:word_end]
            + "◀"
            + raw_contents[word_end:context_end]
        )
        return context.replace("\r", "").replace("\n", "").replace("\t", "")


def post_to_yahoo(query):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Yahoo AppID: {}".format(os.getenv("YAHOO_APPID")),
    }
    param_dic = {
        "id": "temp-1234-5678",
        "jsonrpc": "2.0",
        "method": "jlp.kouseiservice.kousei",
        "params": {"q": query},
    }
    params = json.dumps(param_dic).encode()
    req = request.Request(
        "https://jlp.yahooapis.jp/KouseiService/V2/kousei", params, headers
    )
    with request.urlopen(req) as res:
        body = res.read()
    return body.decode()


def main(page: ft.Page):
    page.title = "テキスト校正"
    page.theme_mode = "light"

    pasted_str = ft.Ref[ft.Text]()
    ok_message = ft.Ref[ft.Text]()
    result_table = ft.Ref[ft.DataTable]()
    copy_button = ft.Ref[ft.ElevatedButton]()

    COLUMNS = [
        "問題の箇所（改行等無視）",
        "修正提案",
        "指摘理由",
        "備考",
    ]

    def reset_result_table():
        result_table.current.columns.clear()
        result_table.current.rows.clear()
        page.update()

    def update_result_table(suggests):
        result_table.current.columns = [ft.DataColumn(ft.Text(c)) for c in COLUMNS]
        table_rows = []
        for suggest in suggests:
            su = Suggest(suggest)
            context = su.get_context(pasted_str.current.value)
            table_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(context)),
                        ft.DataCell(ft.Text(su.fix_suggestion)),
                        ft.DataCell(ft.Text(su.rule)),
                        ft.DataCell(ft.Text(su.note)),
                    ]
                )
            )
        result_table.current.rows = table_rows
        page.update()

    def reset_ok_message():
        ok_message.current.visible = False
        ok_message.current.value = ""
        page.update()

    def update_ok_message(s):
        ok_message.current.visible = True
        ok_message.current.value = s
        page.update()

    def reset_copy_button():
        copy_button.current.text = ""
        copy_button.current.visible = False
        page.update()

    def update_copy_button(s):
        copy_button.current.text = s
        copy_button.current.visible = True
        page.update()

    def exec_proof(_):
        reset_ok_message()

        if len(pasted_str.current.value.strip()) < 1:
            return
        res = post_to_yahoo(pasted_str.current.value)
        suggests = json.loads(res)["result"]["suggestions"]

        reset_copy_button()
        reset_result_table()
        if len(suggests) < 1:
            update_ok_message("問題は見あたりません")
            return
        update_result_table(suggests)
        update_copy_button("結果をコピーする！")

    def copy_table(_: ft.ControlEvent):
        lines = ["\t".join(COLUMNS)]
        for r in result_table.current.rows:
            lines.append("\t".join([c.content.value for c in r.cells]))
        page.set_clipboard(os.linesep.join(lines))
        update_copy_button("結果をコピーしました")

    ui_cols = [
        ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text("校正支援ツール", size=20, weight=ft.FontWeight.BOLD),
                    alignment=ft.alignment.top_left,
                ),
                ft.Container(
                    content=ft.IconButton(
                        icon=ft.icons.SOURCE_OUTLINED,
                        icon_color=ft.colors.BLUE_400,
                        on_click=lambda _: open(
                            "https://github.com/AWtnb/flet-yahoo-proof-api"
                        ),
                    ),
                    alignment=ft.alignment.top_right,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        ft.TextField(
            ref=pasted_str,
            label="ここに入力",
            multiline=True,
            autofocus=True,
            max_lines=6,
            value="セキュリティーは食べれる",
        ),
        ft.FilledButton("校正を依頼する", on_click=exec_proof),
        ft.Divider(),
        ft.Text(ref=ok_message, visible=False, value=""),
        ft.FilledButton(ref=copy_button, on_click=copy_table, visible=False),
        ft.ListView(controls=[ft.DataTable(ref=result_table)], height=250),
    ]

    page.add(ft.Column(controls=ui_cols))


ft.app(target=main)
