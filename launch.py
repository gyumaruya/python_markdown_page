#!/usr/bin/python3
"""Quickly launch a local web server from a directory.

Generate by OpenAI-chatGPT + Github Copilot.
"""
import argparse
import http.server
import socketserver
import markdown
import os


class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    """MarkdownファイルをHTMLに変換して表示するハンドラ.
    
    Markdownファイルのパスを取得し、MarkdownをHTMLに変換して表示する.
    Markdownファイルのパスは、URLのパスから取得する.
    例えば、http://localhost:8080/README.md にアクセスした場合、
    README.mdを表示する.
    """

    def do_GET(self):
        """GETリクエストを処理する."""
        # パスを取得
        path = self.path

        # パスの末尾が/の場合、index.htmlまたは同名の.mdファイルを探す
        # それ以外の場合、そのままのパスでファイルを探す
        # ファイルが見つからない場合、ディレクトリの一覧を表示する
        # ファイルが見つかった場合、MarkdownをHTMLに変換して表示する
        # ファイルが見つからなかった場合、通常のハンドラに委譲する
        if path.endswith('/'):
            index_path = os.path.join(os.getcwd(), path[1:], 'index.html')
            md_name = os.path.basename(path.rstrip('/')) + '.md'
            md_path = os.path.join(os.getcwd(), path[1:], md_name)

            if os.path.exists(index_path):
                path = os.path.join(path, 'index.html')
            elif os.path.exists(md_path):
                path = os.path.join(path, md_name)
            else:
                # ファイルの一覧を表示
                file_list = os.listdir(os.path.join(os.getcwd(), path[1:]))
                file_links = [f"<a href='{path}{file}'>{file}</a>" for file in file_list]
                html_list = "<br>".join(file_links)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(html_list.encode('utf-8'))
                return

        # Markdownファイルの場合、MarkdownをHTMLに変換して表示する
        if path.endswith('.md'):
            # Markdownファイルのパスを取得
            md_file_path = os.path.join(os.getcwd(), path[1:])
            
            # Markdownファイルを読み込む
            with open(md_file_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # MarkdownをHTMLに変換
            html_content = markdown.markdown(md_content)
            
            # パンくずリストを生成
            breadcrumbs = self.generate_breadcrumbs(path)
            
            # パンくずリストとindex.htmlへのリンクを追加
            full_html = f"""
            {breadcrumbs}
            <hr>
            {html_content}
            <hr>
            <a href="/index.html">Home</a>
            """
            
            # HTMLをレスポンスとして返す
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(full_html.encode('utf-8'))
        else:
            # それ以外のリクエストは通常のハンドラに委譲
            super().do_GET()

    def generate_breadcrumbs(self, path):
        """パンくずリストを生成する.
        
        パンくずリストは、以下のような形式で生成する.
        Home / dir1 / dir2 / dir3
        
        Args:
            path (str): パンくずリストを生成するパス.
            
        Returns:
            str: 生成したパンくずリスト.
        """
        parts = path.split('/')
        
        # 同名.mdを表示しているとき、またはindex.htmlを表示しているときのディレクトリ名を削除
        if parts[-1] == "index.html" or parts[-1].rstrip('.md') == parts[-2]:
            parts = parts[:-1]
        
        breadcrumbs = ["<a href='/'>Home</a>"]
        for i, part in enumerate(parts[1:-1]):
            if part:  # 空の部分をスキップ
                breadcrumbs.append(f"<a href='{'/'.join(parts[:i+2])}'>{part}</a>")
        return " / ".join(breadcrumbs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("markdown server")
    parser.add_argument(
        "--bind",
        "-b",
        default="127.0.0.1",
        help="Specify alternate bind address " "[default: loopback address]",
    )
    parser.add_argument("port", default=8080, type=int, nargs="?", help="Specify alternate port [default: 8080]")

    args = parser.parse_args()
    with socketserver.TCPServer((args.bind, args.port), MyHttpRequestHandler) as httpd:
        print(f"Server started at http://{args.bind}:{args.port}")
        httpd.serve_forever()
