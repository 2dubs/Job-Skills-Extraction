# Motivation

You think you know all the skills you need to get the job you are applying to, but do you actually? You think HRs are the ones who take the first look at your resume, but are you aware of something called ATS, aka. Application Tracking System? This project aims to provide a little insight to these two questions, by looking for hidden groups of words taken from job descriptions. 

# Background

This project depends on Tf-idf, term-document matrix, and Nonnegative Matrix Factorization (NMF).

**First**, documents are tokenized and put into term-document matrix, like the following:

![image of term-document matrix](http://mlg.postech.ac.kr/static/research/nmf_cluster1.PNG)

(source: http://mlg.postech.ac.kr/research/nmf)

Each column correponds to a specifica job description (document) while each row corresponds to a skill (feature). 

*Note: Selecting features is a very crucial step in this project, since it determines the pool from which job skill topics are formed. Discussion can be found in the next sessioin.*


**Next**, each cell in term-document matrix is filled with tf-idf value.

 - tf: term-frequency measures how many times a certain word appears in **one** specific document.
 - df: document-frequency measures how many times a certain word appreas across **all** documents
 - idf: inverse document-frequency is a logarithmic transformation of the inverse of document frequency. 

(wikipedia: https://en.wikipedia.org/wiki/Tf%E2%80%93idf)


**Finally**, NMF is used to find two matrices W (m x k) and H (k x n) to approximate term-document matrix A, size of (m x n).  
 - m equals number of featrues (job skills)
 - n equals number of documents (job descriptions)
 - k equals number of components (groups of job skills). 
 
The following is a simple demonstration: 

![image of NMF at work](https://github.com/victorx98/related_job_skills/blob/master/NMF%20BigPicture.png)

Each column in matrix W represents a topic, or a cluster of words. It can be viewed as a set of bases from which a document is formed.  

Each column in matrix H represents a document as a cluster of topics, which are cluster of words. It can be viewed as a set of weights of each topic in the formation of this document. 

# Synopsis

First let's talk about dependencies of this project:
 - NLTK: for tokenization and stop_words
 - Scikit-learn: for creating term-document matrix, NMF algorithm
 
The process consists of three steps:

1. Pulling job description data from online or SQL server. Cleaning data and store data in a tokenized fasion. 
2. Use scikit-learn to create the tf-idf term-document matrix from the processed data from last step. Generate features along the way, or import features gathered elsewhere. 
3. Use scikit-learn NMF to find the (features x topics) matrix and subsequently print out groups based on pre-determined number of topics. 

The following is the process of this project:

<img src="https://github.com/victorx98/related_job_skills/blob/master/Process.png" height="550" width="500">

Yellow section refers to part 1. Blue section refers to part 2. Green section refers to part 3.


# Discussion

Following the 3 steps process from last section, our discussion talks about different problems that were faced at each step of the process. 


## In Data Cleaning ...

1. This section is all about cleaning the job descriptions gathered from online. Extracting texts from HTML code should be done with care, since if parsing is not done correctly, incidents such as `experience in accounting` will be wrongfully parsed as `experienceaccounting`
2. One should also consider how and what punctuations should be handled. Since this project aims to extract groups of skills required for a certain type of job, one should consider the cases for Computer Science related jobs. Examples like `C++` and `.Net` differentiate the way parsing is done in this project, since dealing with other types of documents (like novels,) one needs not consider punctuations. 
3. Another crucial consideration in this project is the definition for documents. This project examines three type. 
    - First, each job description counts as a document. This is the most intuitive way. 
    - Secondly, the idea of n-gram is used here but in a sentence setting. 3 sentences in sequence are taken as a document. For example, if a job description has 7 sentences, 5 documents of 3 sentences will be generated. The reason behind this document selection originates from an observation that each job description consists of sub-parts: Company summary, job description, skills needed, equal employment statement, employee benefits and so on. We are only interested in the skills needed section, thus we want to separate documents in to chuncks of sentences to capture these subgroups. If three sentences from two or three different sections form a document, the result will likely be ignored by NMF due to the small correlation among the words parsed from the document. 
    - Finally, each sentence in a job description can be selected as a document for reasons similar to the second methodology. However, the existing but hidden correlation between words will be lessen since companies tend to put different kinds of skills in different sentences.



## In Feature Selection ...

From the diagram above we can see that two approaches are taken in selecting features.

###### Approach 1
When putting job descriptions into term-document matrix, tf-idf vectorizer from scikit-learn automatically selects features for us, based on the pre-determined number of features. Three key parameters should be taken into account, `max_df` , `min_df` and `max_features`. `max_df` and `min_df` can be set as either float (as percentage of tokenized words) or integer (as number of tokenized words). 

    - `max_df` helps eliminate the confounding effect of words that appear frequently across all documents such as "work" and "create"
    - `min_df` deals with words that appear too rarely, such as typos. Of course, words such as "we","are" and "in" are already taken care of by stop word exclusion (in the data cleaning step and tf-idf vectorizer) to limit the amount of high-df words.
    - `max_features` dictates how many features are taken into consideration based on its tf ranking across documents, which is primarily for reducing runtime. 

By adopting this approach, we are giving the program autonomy in selecting features based on pre-determined parameters. This way we are limiting human interference, by relying fully upon statistics. 


However, this method is far from perfect, since the original data contain a lot of noise. 
The set of stop words on hand is far from complete. Since we are only interested in the job skills listed in each job descriptions, other parts of job descriptions are all factors that may affect result, which should all be excluded as stop words. 
   
For example, a lot of job descriptions contain equal employment statements. This is indeed a common theme in job descriptions, but given our goal, we are not interested in those. The original approach is to gather the words listed in the result and put them in the set of stop words. However, this approach did not eradicate the problem since the variation of equal employment statement is beyond our ability to manually handle each speical case. 

`Topic #7: 
status,protected,race,origin,religion,gender,national origin,color,national,veteran,disability,employment,sexual,race color,sex`

###### Approach 2

Through trials and errors, the approach of selecting features (job skills) from outside sources proves to be a step forward. 
Many websites provide information on skills needed for specific jobs. We gathered nearly 7000 skills, which we used as our features in tf-idf vectorizer. The result is much better compared to generating features from tf-idf vectorizer, since noise no longer matters since it will not propagate to features. 

In the following example, we'll take a peak at approach 1 and approach 2 on a set of software engineer job descriptions:

###### Comparison

**In approach 1**, we see some meaningful groupings such as the following:

in `50_Topics_SOFTWARE ENGINEER_no vocab.txt` 

`Topic #13: 
sql,server,net,sql server,c#,microsoft,aspnet,visual,studio,visual studio,database,developer,microsoft sql,microsoft sql server,web`

However, the majorities are consisted of groups like the following:

`Topic #15: 
ge,offers great professional,great professional development,professional development challenging,great professional,development challenging,ethnic expression characteristics,ethnic expression,decisions ethnic,decisions ethnic expression,expression characteristics,characteristics,offers great,ethnic,professional development`

`Topic #16: 
human,human providers,multiple detailed tasks,multiple detailed,manage multiple detailed,detailed tasks,developing generation,rapidly,analytics tools,organizations,lessons learned,lessons,value,learned,eap`

As I have mentioned above, this happens due to incomplete data cleaning that keep sections in job descriptions that we don't want. 
 


 **In approach 2**, since we have pre-determined the set of features, we have completely avoided the second situation above. Examples of groupings include:
 
in `50_Topics_SOFTWARE ENGINEER_with vocab.txt`

`Topic #4: 
agile,scrum,sprint,collaboration,jira,git,user stories,kanban,unit testing,continuous integration,product owner,planning,design patterns,waterfall,qa`

`Topic #6: 
java,j2ee,c++,eclipse,scala,jvm,eeo,swing,gc,javascript,gui,messaging,xml,ext,computer science`

`Topic #24: 
cloud,devops,saas,open source,big data,paas,nosql,data center,virtualization,iot,enterprise software,openstack,linux,networking,iaas`

`Topic #37: 
ui,ux,usability,cross-browser,json,mockups,design patterns,visualization,automated testing,product management,sketch,css,prototyping,sass,usability testing`


The method has some shortcomings too. First, it is not at all complete. Since tech jobs in general require many different skills as accountants, the set of skills result in meaningful groups for tech jobs but not so much for accounting and finance jobs. Secondly, this approach needs a large amount of maintnence. The technology landscape is changing everyday, and manual work is absolutely needed to update the set of skills.

(* Complete examples can be found in the **EXAMPLE** folder *)


# In the future...

Turns out the most important step in this project is cleaning data. In this project, we only handled data cleaning at the most fundamental sense: parsing, handling punctuations, etc. However, it is important to recognize that we don't need every section of a job description. The target is the "skills needed" section. To extract this from a whole job description, we need to find a way to recognize the part about "skills needed." The following is an idea for futrure works...


This is an idea based on the assumption that job descriptions are consisted of multiple parts such as company history, job description, job requirements, skills needed, compensation and benefits, equal employment statements, etc. To dig out these sections, three-sentence paragraphs are selected as documents. (Three-sentence is rather arbitrary, so feel free to change it up to better fit your data.) We assume that among these paragraphs, the sections described above are captured. Thus, running NMF on these documents can unearth the underlying groups of words that represent each section. This is still an idea, but this should be the next step in fully cleaning our initial data. Once groups of words that represent sub-sections are discovered, one can group different paragraphs together, or even use machine-learning to recognize subgroups using "bag-of-words" method. 

# License

3-Clause BSD
