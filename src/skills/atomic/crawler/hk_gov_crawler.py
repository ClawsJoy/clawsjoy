"""香港政府网站专用爬虫 - 入境处、一站通等"""
import requests
from bs4 import BeautifulSoup
import re
import time
import json
from urllib.parse import urljoin, urlparse
from datetime import datetime
import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')
from src.lib.vector.vector_manager import vector_manager

class HKGovCrawlerSkill:
    name = "hk_gov_crawler"
    description = "香港政府网站专用爬虫（入境处、一站通等）"
    version = "1.0.0"
    category = "crawler"
    
    # 香港政府网站种子URL
    SEED_URLS = {
        "immd": "https://www.immd.gov.hk/hkt/index.html",           # 入境处首页
        "immd_online": "https://www.immd.gov.hk/hkt/online-services/", # 网上服务
        "govhk": "https://www.gov.hk/tc/residents/",                 # 一站通居民版
        "immd_useful": "https://www.immd.gov.hk/hkt/useful_information/", # 有用资料
        "immd_sitemap": "https://www.immd.gov.hk/hkt/sitemap.html",  # 网站地图
    }
    
    # 内容优先级关键词
    PRIORITY_KEYWORDS = {
        "high": ["签证", "进入许可", "高才通", "优才", "专才", "人才入境", "申请资格"],
        "medium": ["身份证", "居留权", "护照", "旅行证件", "登记", "证明"],
        "low": ["表格下载", "办事地址", "办公时间", "常见问题"]
    }
    
    def execute(self, params):
        target = params.get("target", "immd")  # immd, govhk, all
        max_pages = params.get("max_pages", 30)
        max_depth = params.get("max_depth", 2)
        
        # 确定种子URL
        if target == "all":
            seed_urls = list(self.SEED_URLS.values())
        else:
            seed_urls = [self.SEED_URLS.get(target, self.SEED_URLS["immd"])]
        
        print(f"🌐 目标站点: {target}")
        print(f"📊 种子URL: {seed_urls}")
        
        all_results = []
        for seed_url in seed_urls:
            print(f"\n📄 爬取: {seed_url}")
            results = self._crawl_site(seed_url, max_pages, max_depth)
            all_results.extend(results)
        
        return {
            "success": True,
            "target": target,
            "total_crawled": len(all_results),
            "results": all_results,
            "message": f"完成爬取，新增 {len(all_results)} 条知识"
        }
    
    def _crawl_site(self, seed_url, max_pages, max_depth):
        """爬取单个站点"""
        visited = set()
        to_visit = [(seed_url, 0)]
        results = []
        page_count = 0
        
        while to_visit and page_count < max_pages:
            url, depth = to_visit.pop(0)
            
            if url in visited or depth > max_depth:
                continue
            visited.add(url)
            
            try:
                print(f"  📄 [{depth}] {url[:80]}...")
                
                resp = requests.get(url, timeout=30, headers={
                    'User-Agent': 'ClawsJoy-HK-Gov-Crawler/1.0',
                    'Accept-Language': 'zh-HK,zh-CN;q=0.9,zh;q=0.8'
                })
                
                if resp.status_code != 200:
                    continue
                
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # 提取正文
                for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                    tag.decompose()
                
                text = soup.get_text()
                text = re.sub(r'\s+', ' ', text).strip()
                
                # 提取标题
                title = ""
                if soup.title:
                    title = soup.title.string
                elif soup.find('h1'):
                    title = soup.find('h1').get_text()
                
                # 判断优先级
                priority = self._get_priority(text)
                
                # 存入向量库（只存有实质内容且优先级不是low的）
                if len(text) > 300 and priority != "low":
                    doc_id = vector_manager.add_knowledge(
                        text[:3000],
                        category="hk_gov",
                        metadata={
                            "source_url": url,
                            "title": title,
                            "site": self._get_site_name(url),
                            "priority": priority,
                            "crawled_at": datetime.now().isoformat()
                        }
                    )
                    
                    page_count += 1
                    results.append({
                        "url": url,
                        "title": title[:100] if title else "",
                        "priority": priority,
                        "content_length": len(text),
                        "vector_id": doc_id
                    })
                    
                    print(f"      ✅ 存入 ({priority}优先级)")
                
                # 提取新链接
                if depth < max_depth:
                    links = self._extract_links(soup, url)
                    for link in links:
                        if link not in visited and self._is_relevant_url(link):
                            to_visit.append((link, depth + 1))
                
                time.sleep(1)  # 礼貌延迟
                
            except Exception as e:
                print(f"      ❌ 错误: {e}")
                continue
        
        return results
    
    def _get_priority(self, text):
        """判断内容优先级"""
        text_lower = text.lower()
        for priority, keywords in self.PRIORITY_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    return priority
        return "low"
    
    def _get_site_name(self, url):
        """获取站点名称"""
        if "immd.gov.hk" in url:
            return "入境事务处"
        elif "gov.hk" in url:
            return "政府一站通"
        else:
            return "其他"
    
    def _extract_links(self, soup, base_url):
        """提取相关链接"""
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('#') or href.startswith('javascript:'):
                continue
            if href.startswith('mailto:') or href.startswith('tel:'):
                continue
            
            full_url = urljoin(base_url, href)
            
            # 只保留同域名链接
            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                links.append(full_url)
        
        # 去重并限制数量
        return list(dict.fromkeys(links))[:30]
    
    def _is_relevant_url(self, url):
        """判断URL是否相关"""
        # 排除多媒体文件
        exclude_patterns = [r'\.(jpg|png|gif|pdf|zip|mp4)$', r'\?format=']
        for pattern in exclude_patterns:
            if re.search(pattern, url, re.I):
                return False
        return True

skill = HKGovCrawlerSkill()
