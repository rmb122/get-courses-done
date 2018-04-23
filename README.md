## 没事做的玩的试题库助手

其实学长已经有写好的了, 主要是顺便练一下 BeautifulSoup, 2333.  
只支持单选和判断题.  
而且需要注意在碰到 `如下：` 开头的题目会因为被其他同样开头的题目覆盖掉, 导致错误,   
不过错的不会很多, 最多一两个.  

### 使用方法

将 cookie 以 json 保存在同目录下的 cookie.json 后  
再将试题的表格放在同目录下, 最后把    
```python
st = sheet(["1.xls", "2.xls"])
```
这个 list 中的表格名字替换掉之后就可以运行啦.   

PS: 导出 cookie 我用的是 chrome 下的 [EditThisCookie][1] 插件.  
PSS: 最后别忘了提交作业, 我只做了做题的部分, 不会自动提交作业.

[1]: https://chrome.google.com/webstore/detail/fngmhnnpilhplaeedifhccceomclgfbg