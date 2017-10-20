# RecursiveCrawler
RecursiveCrawler is an application that recursively crawls urls from a website.
The user can specify the number of concurrent requests that can be made. 
The user is also be able to specify a `download_delay` that each worker will respect when making the requests. 
Also provides the ability to specify the maximum number of urls to visit. 
The spider does not visit the same url twice.

And finally display the total number of unique pages visited and bytes downloaded. 
