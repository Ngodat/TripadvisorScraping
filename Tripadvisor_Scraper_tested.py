import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import io

# params
# gecko_path = r'D:\\setup\\geckodriver\\geckodriver'
gecko_path = '/usr/local/bin/geckodriver'  
options = webdriver.firefox.options.Options()
options.headless = False 

## to edit
airlines = ['British Airways'
            # ,'Mongolia Airline'
            # ,'easyJet'
            ] #to add full list of airline names
startPagesDetail = ['https://www.tripadvisor.co.uk/ShowUserReviews-g1-d8729039-r799548098-British_Airways-World.html'
                    # ,'https://www.tripadvisor.co.uk/ShowUserReviews-g1-d13804006-r718578415-Aero_Mongolia-World.html'                    
                    # ,'https://www.tripadvisor.co.uk/ShowUserReviews-g1-d8729066-r799564557-EasyJet-World.html'                    
                   ] # to add the first detailed review's url for each airline 

startPagesBrief = ['https://www.tripadvisor.co.uk/Airline_Review-d8729039-Reviews-British-Airways'
                    # ,'https://www.tripadvisor.co.uk/Airline_Review-d13804006-Reviews-Aero-Mongolia'                    
                    # ,'https://www.tripadvisor.co.uk/Airline_Review-d8729066-Reviews-EasyJet'
                    ] # to add the first brief review page for each airline
maxPage = 100                # maximum no of pages to crawl
savingInterval = 3          # number of pages to save 
waitingTime = 2             # maximum waiting time in seconds
detailCrawlingMode = 'startOver' # if wanna continue crawl starting from a specific page, change detailCrawlingMode to 'continue'
# detailCrawlingMode = 'continue'

########################

## define functions
def detailScraper(startUrl, airline, mode):
    global maxPage, savingInterval, waitingTime
    dataDetail = dict()                                                                 # create an empty dictionary to keep data
    filenameDetail = os.path.join(os.getcwd(),airline + '_detail.txt')                  # set the output file directory                          
    driver = webdriver.Firefox(options = options, executable_path = gecko_path)         # call the driver
    driver.get(startUrl)                            
    time.sleep(2)
    try:                                                                       # sleep 2 seconds for the first page to load and click English Langugage
        driver.find_element_by_xpath('//*[@id = "_evidon-accept-button"]').click()           # click accept cookie
    except:
        pass
    time.sleep(2)
    if mode == 'startOver':
        driver.find_element_by_xpath('//input[@id = "taplc_location_review_filter_controls_sur_0_filterLang_en"]').click()   # select English language
        time.sleep(2)
    sleepingTime = 0; lastPageReached = 0; currentPage = 0                     # set other initial params  
    print('Start crawling {0} detailed reviews'.format(airline))                        # inform users crawling started
    while currentPage < maxPage:
        while True:
            time.sleep(0.5)
            try:
                if len(driver.find_elements_by_xpath('//div[@class = "ui_button primary disabled"]')) == 1:
                    lastPageReached = 1
                if (len(driver.find_elements_by_xpath('//div[@class = "ui_button primary "]')) > 0 or lastPageReached == 1) and \
                int(driver.find_element_by_xpath('//div[@class = "pageNumbers"]/a[contains(@class, "current")]').text) == currentPage + 1: 
                    selPage = Selector(text = driver.page_source)
                    break
            except:
                continue

        currentPage = int(selPage.xpath('//div[@class = "pageNumbers"]/a[contains(@class, "current")]/text()').extract_first())
        print ("=============page {0}=============".format(currentPage))
        for sel in selPage.xpath('//div[@class = "reviewSelector"]'):                   # select data
            reviews = '; '.join(sel.xpath('.//p[@class = "partial_entry"]//text()').extract())
            reviewsQuote = sel.xpath('.//span[@class = "noQuotes"]/text()').extract_first()   
            travelDate = ''.join(sel.xpath('.//div[@class = "prw_rup prw_reviews_stay_date_hsx"]//text()').extract()).replace('Date of travel:','')
            rateGeneral = sel.xpath('.//div[@class = "rating reviewItemInline"]/span[1]/@class').extract_first().replace('ui_bubble_rating bubble_','')
            rateDetail = '|'.join([a +':'+ b[-2:] for a,b in zip(sel.xpath('.//li[@class = "recommend-answer"]/div[2]/text()').extract(),
                sel.xpath('.//li[@class = "recommend-answer"]/div[1]/@class').extract())])
            userLocation = sel.xpath('.//span[@class = "expand_inline userLocation"]/text()').extract_first()
            name = sel.xpath('.//span[@class = "expand_inline scrname"]/text()').extract_first()
            reviewDate = sel.xpath('.//span[@class = "ratingDate relativeDate"]/@title').extract_first()
            reviewThanks = str(sel.xpath('.//span[@class = "numHelp emphasizeWithColor"]/text()').extract_first()).replace(' \xa0','')
            reviewId = sel.xpath('./@data-reviewid').extract_first()
            reviewUrl = 'https://www.tripadvisor.co.uk/' + sel.xpath('.//div[@class = "wrap"]/div/a/@href').extract_first()
            contribution = sel.xpath('.//div[@class = "memberBadgingNoText"]/span[@class ="ui_icon pencil-paper"]/following-sibling::span/text()').extract_first()
            helpfulVotes = sel.xpath('.//div[@class = "memberBadgingNoText"]/span[@class ="ui_icon thumbs-up"]/following-sibling::span/text()').extract_first()
            language = sel.xpath('.//span[@class = "ui_button secondary small" and text() = "Google Translation "]/@data-url').extract_first()
            if language is None:
                language = 'en'
            else:
                language = language[-8:-6]
            dataDetail[airline+'_'+reviewId] = {'reviewId':reviewId,'reviewUrl':reviewUrl,'contribution':contribution,'helpfulVotes':helpfulVotes
            ,'username':name,'userLocation':userLocation,'reviews':reviews, 'reviewsQuote': reviewsQuote
            ,'reviewThanks':reviewThanks,'travelDate':travelDate, 'reviewDate': reviewDate, 'rateGeneral': rateGeneral
            , 'rateDetail': rateDetail,'scrapingPageNo':currentPage, 'language': language, 'airline':airline} # save all info crawled above into a dictionary

        # save every n pages
        if int(currentPage)%savingInterval == 0: 
            with open(filenameDetail, "a", encoding="utf-8") as file:     # open a new txt file to append n pages
                file.write(str(dataDetail) + '\n')      # save append data of n pages
                file.close()
                dataDetail = dict() #empty the dic

        # break if reaching the last page or reach the maxPage, save the remaining data if not saved
        if lastPageReached == 1 or currentPage == maxPage:
            if currentPage%savingInterval != 0:
                with open(filenameDetail, "a", encoding = 'utf-8') as file: 
                    file.write(str(dataDetail) + '\n')  
                    file.close()
            break          

        # click the next button
        nextButtonClicked = 0                           # next button not clicked yet
        while nextButtonClicked != 1:                   # wait until next button is clickable and clicked
            try:
                driver.find_element_by_xpath('//div[@class = "ui_button primary "]').click()
                sleepingTime = 0            # reset sleeping time for each new page
                nextButtonClicked = 1       # set the flag to 1 to stop the loop
            except Exception as e:
                time.sleep(0.5)
                sleepingTime += 0.5
                if sleepingTime > waitingTime:
                    break
        if sleepingTime > waitingTime:
            break
    driver.quit()

def briefScraper(startUrl, airline):
    global maxPage, savingInterval, waitingTime
    dataBrief = dict()
    filenameBrief = os.path.join(os.getcwd(),airline + '_brief.txt')
    driver = webdriver.Firefox(options = options, executable_path = gecko_path)
    driver.get(startUrl)
    time.sleep(2)
    try:
        driver.find_element_by_xpath('//*[@id = "_evidon-accept-button"]').click()           # click accept cookie
    except:
        pass
    sleepingTime = 0; lastPageReached = 0; currentPage = 0; ind = 0; lastId = ""

    print('Start crawling {0} brief reviews'.format(airline))

    while currentPage < maxPage:
        while True:
            time.sleep(0.5)
            try:
                if len(driver.find_elements_by_xpath('//span[@class = "ui_button nav next primary disabled"]')) == 1:
                    lastPageReached = 1
                if (len(driver.find_elements_by_xpath('//a[@class = "ui_button nav next primary "]')) > 0 or lastPageReached == 1) and \
                driver.find_elements_by_xpath('//div[@class = "oETBfkHU"]')[-1].get_attribute('data-reviewid') != lastId:
                    selPage = Selector(text = driver.page_source)
                    break                    
            except:
                continue
        
        currentPage = int(selPage.xpath('//div[@class = "pageNumbers"]/span[contains(@class,"current")]/text()').extract_first())
        lastId = selPage.xpath('//div[@class = "oETBfkHU"]/@data-reviewid')[-1].extract()
        print ("=============page {0}=============".format(currentPage))
        for sel in selPage.xpath('//div[@class = "oETBfkHU"]'):
            reviewId = sel.xpath('./@data-reviewid').extract_first()
            tripDestination = sel.xpath('.//div[@class = "hpZJCN7D"]/div[1]/text()').extract_first()
            flightType = sel.xpath('.//div[@class = "hpZJCN7D"]/div[2]/text()').extract_first()
            flightClass = sel.xpath('.//div[@class = "hpZJCN7D"]/div[3]/text()').extract_first()
            ind += 1
            dataBrief[airline+'_'+reviewId] = {'reviewId':reviewId,'tripDestination':tripDestination,'flightType':flightType
            ,'flightClass':flightClass,'scrapingPageNo':currentPage}

        # save every n pages
        if currentPage%savingInterval == 0: 
            with open(filenameBrief, "a",encoding="utf-8") as file: #open a new txt file to append 30 pages
                file.write(str(dataBrief) + '\n') # save append data of 30 pages
                file.close()
                dataBrief = dict() #empty the dic

        # break if reaching the last page
        if lastPageReached == 1 or currentPage == maxPage:
            if currentPage%savingInterval != 0: #saving remained pages
                with open(filenameBrief, "a", encoding = 'utf-8') as file: #open a new txt file to append 30 pages
                    file.write(str(dataBrief) + '\n') # save append data of 30 pages#
                    file.close()
            driver.quit()
            break  
        
        # click the next button
        nextButtonClicked = 0
        while nextButtonClicked != 1:
            try:
                driver.find_element_by_xpath('//a[@class = "ui_button nav next primary "]').click()
                sleepingTime = 0            # reset sleeping time for each new page
                nextButtonClicked = 1       # set the flag to 1 to stop the loop
            except Exception as e:
                time.sleep(0.5)
                sleepingTime += 0.5
                if sleepingTime > waitingTime/2:
                    break
        if sleepingTime > waitingTime:
            break
    driver.quit()


if __name__ == '__main__':
    for url, airline in zip(startPagesDetail, airlines):
        detailScraper(url,airline,detailCrawlingMode)
    for url, airline in zip(startPagesBrief, airlines):
        briefScraper(url,airline)

# WHAT TO ADJUST: LINES IN SECTION 'TO EDIT'
# ERASE TXT FILES BEFORE RUN