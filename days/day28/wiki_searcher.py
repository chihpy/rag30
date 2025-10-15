import wikipedia

class WikiSearcher:
    def __init__(self, language="zh"):
        wikipedia.set_lang(language)  # 設定語言，例如中文
        self.cache = {}

    def search_keyword(self, keyword):
        """
        查詢單個關鍵字
        返回字典: {title, url, summary}，找不到返回 None
        """
        if keyword in self.cache:
            return self.cache[keyword]

        try:
            page = wikipedia.page(keyword, auto_suggest=False)
            data = {
                "title": page.title,
                "url": page.url,
                "summary": page.summary,
                "content": page.content,
            }
            # 快取結果
            self.cache[keyword] = data
            self.cache[page.title] = data
            return data
        except wikipedia.DisambiguationError as e:
#            print(f'{keyword}: 多義詞')
            # 多義詞，返回可能選項列表
            #self.cache[keyword] = {"title": None, "url": None, "summary": None, "options": e.options}
            self.cache[keyword] = None
            return None
        except wikipedia.PageError:
#            print(f'{keyword}: 找不到頁面')
            # 找不到頁面
            self.cache[keyword] = None
            return None
        except Exception as e:
#            print(f'{keyword}: 其他錯誤')
            # 其他錯誤
            self.cache[keyword] = None
            return None

    def search_keywords(self, keywords):
        """
        批量查詢關鍵字
        返回字典 {keyword: data}
        """
        results = {}
        for kw in keywords:
            results[kw] = self.search_keyword(kw)
        return results

if __name__ == "__main__":
    keywords = ['勒贝格控制收敛定理']

    wiki_searcher = WikiSearcher(language="zh")

    search_result = wiki_searcher.search_keywords(keywords)
    print(search_result)