# Board Game Recommendation and Rental System

## Introduction
Our main motivation behind our project was to develop a program that could be used by anyone to not only play their favorite board games, but also expand their horizons and enjoy new board games similar to their current tastes. We hoped that individuals would continuously use this program to eventually try a multitude of different board game types, and ultimately develop a vast network of games to share with others. Our program is a simple, yet efficient way of encouraging individuals to try new things that may or may not be outside of their comfort zone. Additionally, in an age where we are surrounded by technology, board games provide an escape from the constant media consumption that follows social media, streaming services, etc. We hoped to promote more authentic ways to connect with others beyond our computer screens, allowing people to create or strengthen their friendships. We hypothesized that our recommendation program would be effective in providing recommended games that would be of interest to the user, yet not be so similar to the games that they usually play. Furthermore, we proposed that our rental system be comprehensive and efficient for users looking for new games. Although there are board game recommendations programs found on the Internet, our system is unique in that it also includes the option to actually play the recommended games via our rental system.

## Neo4j Database Setup
In order to run the recommendation system and the Neo4j API, users must first start Neo4j on their local device through Terminal. Once this neo4j is running, users must also
edit the password.txt file to replace the current password with their Neo4j localhost password and save the file. Users must also insert a copy of the 
csv files used to add the nodes and edges from the repository into their Neo4j import folder on their local device. 

## Redis Database Setup
In order to run the Redis API, users must first start Redis on their local device through Terminal. 

## Program Deployment
In order to return recommendations based on a specific user id and run the rental system implementation, users must first install Neo4j, Redis, and follow 
the corresponding setup directions. Users can then directly run the driver.py file in order to populate Neo4j with nodes and edges, and redis with the game
and user data. These must be run first prior to retrieving recommendations.

## Installations
The following packages used within this project must first be installed (if not already) in order to effectively run the driver.py file. 
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install these to your local environment. 

```bash
pip install pandas
```

Please use the following resources to install Neo4j and redis:
[Redis installation](https://redis.io/docs/getting-started/installation/install-redis-on-mac-os/)
[Neo4j installation](https://neo4j.com/docs/operations-manual/current/installation/osx/)
