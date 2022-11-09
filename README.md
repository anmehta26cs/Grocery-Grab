# Grocery-Grab
> NOTE: This project is still in development. The following is a list of features that are currently being worked on. 
- [x] AWS Deployment
- [x] Link Sharing
- [x] Group Synchronization

## Description

Grocery Grab is a web application that allows users to create a grocery list and share it with others. Users can add items to their list, remove items from their list, and mark items as purchased. Users can also share their list with others by sending them a link to their list. Users can also view other users' lists.

## Installation

To install Grocery Grab, clone the repository and run the following command to install the required modules:

``` pip install -r requirements.txt ```

As of now, Grocery Grab can only be deployed locally. To set up the database, run the following commands:

``` sqlite3 grocerygrab.db ```

``` .read schema.sql ```

``` .exit ```

From the same directory, run the following command to start the server:

``` flask run ```

## Usage
![Grocery Grab](https://github.com/anmehta26cs/Grocery-Grab/blob/main/static/login.png)

![Grocery Grab](https://github.com/anmehta26cs/Grocery-Grab/blob/main/static/groups.png)