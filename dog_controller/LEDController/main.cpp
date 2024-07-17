#include "FaceLightClient.h"

int main(){
    FaceLightClient client;

    client.setAllLed(client.red);
    client.sendCmd();
    int mode = 2;

    switch (mode){
    case 0:
        /* Same Color Test */
        while(true){
            client.setAllLed(client.red);
            client.sendCmd();
            usleep(2000000);
            client.setAllLed(client.green);
            client.sendCmd();
            usleep(2000000);
            client.setAllLed(client.blue);
            client.sendCmd();
            usleep(2000000);
            client.setAllLed(client.yellow);
            client.sendCmd();
            usleep(2000000);
            client.setAllLed(client.black);
            client.sendCmd();
            usleep(2000000);
            client.setAllLed(client.white);
            client.sendCmd();
            usleep(2000000);
        }
        break;
    case 1:
        /* Custom Setting */
        for(int i(0); i < 12; ++i){
            switch (i % 3)
            {
            case 0:
                client.setLedColor(i, client.red);
                break;
            case 1:
                client.setLedColor(i, client.green);
                break;
            case 2:
                client.setLedColor(i, client.blue);
                break;
            default:
                break;
            }
        }
        client.sendCmd();
        break;
    case 2:
        int i = 0;
        int old_i = 11;
        while(true){
            client.setLedColor(i, client.red);
            client.setLedColor(old_i, client.black);
            client.sendCmd();
            usleep(100000);
            old_i = i;
            i = (i+1)%12;
        }
    break;
    }

    return 0;
}

void setup(){
    client = FaceLightClient();
}
FaceLightClient client;

void setLedColor(uint8_t led_id, uint8_t r, uint8_t g, uint8_t b){
    uint8_t color[3] = {r, g, b};
    client.setLedColor(led_id, color);
    client.sendCmd();
}

void setAllLed(uint8_t r, uint8_t g, uint8_t b){
    uint8_t color[3] = {r, g, b};
    client.setAllLed(color);
    client.sendCmd();
}

void clearAllLed(){
    uint8_t color[3] = {0, 0, 0};
    client.setAllLed(color);
    client.sendCmd();
}