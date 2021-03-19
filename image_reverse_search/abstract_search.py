from abc import abstractmethod, ABC
from urllib.parse import unquote

import requests
from pyquery import PyQuery as pq


class ReverseImageInfo:
    def __init__(self, ref_url: str, extra_info: dict):
        self.ref_url = ref_url
        self.extra_info = extra_info

    ref_url: str
    extra_info: dict

    def __repr__(self):
        return f"ReverseImageInfo({self.__dict__})"


class AbstractReverseSearchEngine(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_info_from_search_engine(self, orig_img: str):
        pass

    def search(self, orig_img: str):
        return self.get_info_from_search_engine(orig_img)


class GoogleReverseSearchEngine(AbstractReverseSearchEngine):
    DEFAULT_HEADERS = {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0'}
    DEFAULT_URL = "https://www.google.com/searchbyimage?image_url="

    def __init__(self, headers=None, url=DEFAULT_URL):
        super().__init__()
        if headers is None:
            headers = self.DEFAULT_HEADERS
        self.headers = headers
        self.url = url

    @staticmethod
    def transform(item):
        return ReverseImageInfo(item["imgrefurl"], {
            "height": item["h"],
            "width": item["w"],
            "imgurl": item["imgurl"]
        })

    def get_info_from_search_engine(self, orig_img: str) -> [ReverseImageInfo]:
        r = requests.get(self.url + orig_img, headers=self.headers).text
        res_list = []
        for i in pq(r).find(".g"):
            if pq(i).find("div:has(img)"):
                try:
                    res_list.append(
                        {
                            k[0]: unquote(k[1])
                            for k in [i.split("=") for i in pq(i)
                                                                .find(".rGhul")
                                                                .attr("href")[8:]
                                                                .split("&")]
                        }
                    )
                except Exception:
                    continue
        return list(map(lambda raw_item: self.transform(raw_item), res_list))
