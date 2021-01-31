#include <string.h>
#include <stdio.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include <netinet/in.h>
#include <stdlib.h>
#define MAX 80
#define PORT 2019
#define SA struct sockaddr

int main()
{
   //int connfd.len;
   //struct sockaddr_in r;
   //struct sockaddr_in cli;

 int sockfd = socket(AF_INET, SOCK_STREAM, 0);
 if (sockfd == -1)
  { 
    printf ("Socket Creation: FAIL!\n");
    exit(0);
  }
 else printf ("Epituxhs dhmiourgia Socket\n" );
 struct sockaddr_in servaddr;
 bzero (&servaddr, sizeof(servaddr));
 servaddr.sin_family= AF_INET; 
 servaddr.sin_addr.s_addr = htonl (INADDR_ANY);
 servaddr.sin_port = htons(PORT);
 if ((bind(sockfd, (struct sockaddr*)&servaddr, sizeof(servaddr)))!=0)
   {
      printf("Apotuxhmenh desmeush Socket\n");
      exit(0);
    }
    else printf ("Epituxhmenh desmeush Socket\n");
 if ((listen(sockfd,5)) != 0)
   {
      printf("Den akouei...\n");
      exit(0);
    }
 else printf("O diakomisths akouei....\n");
 struct sockaddr_in cli;
 int len = sizeof(cli);
 int new_socket = accept(sockfd, (struct sockaddr*)&cli, (socklen_t*)&len);
 if (new_socket<0)
  { 
     printf ("Apotuxhmenh sundesh me diakomisth\n");
     exit(0);
   }
  else 
  {
    printf("\n Sundethike neos pelatis \n");
    char buff[]= "hello client";
    write (new_socket, &buff, sizeof(buff));
    printf("%s\n", buff);
    }
  close (sockfd);
  printf("H sundesh xathike\n");
}
