######
### Parsing Poland's farm subsidies detailed data
######
# Load the libraries
# install.packages(c("rvest","tidyverse"))
library(rvest)
library(tidyverse)
options(stringAsFactors=FALSE)
options(dplyr.width=Inf)
# If you are doing this on a VPS such as DO
# You might need to add install.packages("selectr")
# if you use Ubuntu + Docker
# See http://berkorbay.me/documents/R_on_cloud.html

# Each individual record is like http://beneficjenciwpr.minrol.gov.pl/outrecords/prnt/<RECORD ID>
# There are a total of 1430872 records.
# The process can be parallelized or distributed to other computers

agree_to_terms<-function(the_session,the_form){
    #Click on the checkbox
    the_response <- set_values(the_form,`data[Outrecord][accept]`=1)
    #Submit the form
    the_output <- submit_form(the_session,the_response)
    #Return the object
    return(the_output)
}

parse_tables<-function(raw_object,the_id,export_html=TRUE,export_folder="raw_htmls"){

    if(!dir.exists("raw_htmls")){
        dir.create(path=export_folder,showWarnings=FALSE)
    }

    raw_object %>% read_html() %>% write_xml(file=paste0(export_folder,the_id,".html"))

    the_data <-
    cbind(
        data.frame(record_id=the_id),
        data.frame(labels=c("budget_year","first_name","last_name","name","municipality","postal_code"),
        values=raw_object %>% read_html() %>% html_nodes("div.outrecord_data") %>% html_text()) %>%
        tidyr::spread(labels,values),
        data.frame(labels=c(gsub("c_1","c_",paste0("subc_",1001:1101)),"sum"),
        values=raw_object %>% read_html() %>% html_nodes(css=".outrecord_data_green") %>% html_text()) %>%
        tidyr::spread(labels,values)
    )

    return(as.tibble(the_data,validate=FALSE))

}

base_url<-"http://beneficjenciwpr.minrol.gov.pl/outrecords/prnt/"

#Comment the prints if you don't want to get much verbose
# There are a total of 1430872 records.
# It could have been written without the for, but I leave it for another version.
for(the_id in 1:1430872){
    #Comment this if you don't want verbose
    print(paste0("Record ID: ", the_id))
    #Create a session if not exists
    if(!exists("the_session")){
        the_session <- html_session(paste0(base_url,the_id))
    }else{
        #Jump to the next page
        the_session <- the_session %>% jump_to(paste0(base_url,the_id))
    }

    #Check if there is TOC form
    if(length(html_form(the_session))>0){
        print("Agreeing to terms")
        raw_object <- agree_to_terms(the_session,html_form(the_session)[[2]])
    }else{
        raw_object <- the_session
    }

    #Parse the table
    print("Getting the url and parsing")
    data_record <- parse_tables(raw_object,the_id)
    print("Got the data")

    #Create a data.frame if not exists
    if(!exists("aggregate_data")){
        aggregate_data <- data_record
    }else{
        #Otherwise, append
        aggregate_data <- rbind(aggregate_data,data_record)
    }

    #Comment these if you don't want verbose
    print("Success")
    print(aggregate_data)
}
