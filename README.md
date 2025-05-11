# Verbal Dog Training
My master thesis topic was “Verbal training of a robot dog“. In this thesis I have created a program stack that tries to simulate real dog training. There are a few pre programmed actions the dog can perform, and it can either “anonymize” the actions or have a few preloaded commands for them. The usual training was done without any previous knowledge and from scratch.

The robot dog used was the Unitree Go1 with various python libraries. 

A training step goes likes this:
- (optional: Hotword recognition “Hey Techie!” to await actual speaking intent)  
- Speech recognition with “Whisper” (Open-source Speech-to-text from OpenAI)  
- Check if command has confirmed matches  
- Check if command has a small Levenshtein distance to a confirmed command (like “sit” and “sat”)  
- Query the local LLM which command could be used  
- If the LLM fails or picks a confirmed negative, a random action is rolled from the remaining actions  
- The dog executes the picked action  
- The dog awaits Feedback: Listens to “Yes” & “Correct” for positive, and “No” & “Wrong” for the negative feedback  
- The picked Command + Action Combo is memorized  
- The Loop repeats  

The end result was a soft success. The training itself had to rely on quite a bit of randomness, since a very weak and small LLM was used which could’ve accelerated the process immensely. The same goes for the speech recognition, which failed a lot of times and resulted in bogus text recognized. With the stronger models it worked way better, but the calculation time was reduced from practically real time to up to 30 seconds, which was unacceptable in this case.

[![image](https://github.com/user-attachments/assets/f55a4a35-c8c9-413a-8e1b-dded56b4f3f9)](https://youtu.be/rpL5GCnFsEw?si=YNPQ7GYVymjb6Jgh)

![image](https://github.com/user-attachments/assets/511438cc-17f5-4f21-8e9f-4bde94ba85b6)
