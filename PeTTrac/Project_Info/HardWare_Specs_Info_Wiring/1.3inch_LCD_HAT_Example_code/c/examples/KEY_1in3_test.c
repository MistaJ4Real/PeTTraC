#include "DEV_Config.h"
#include "LCD_1in3.h"
#include "GUI_Paint.h"

#include "test.h"

#include <stdlib.h>		//exit()
#include <signal.h>     //signal()

void KEY_1IN3_test(void)
{
    // Uncomment the keystroke example below if you want to run it separately
    // // Exception handling:ctrl + c
    // signal(SIGINT, Handler_1IN3_LCD);
    
    // /* Module Init */
	// if(DEV_ModuleInit() != 0){
    //     DEV_ModuleExit();
    //     exit(0);
    // }
	
    // /* LCD Init */
	// printf("1.3inch LCD demo...\r\n");
	// LCD_1IN3_Init(HORIZONTAL);
	// LCD_1IN3_Clear(WHITE);
    // LCD_SetBacklight(1023);
    
    UWORD *BlackImage;
    UDOUBLE Imagesize = LCD_1IN3_HEIGHT*LCD_1IN3_WIDTH*2;
    printf("Imagesize = %d\r\n", Imagesize);
    if((BlackImage = (UWORD *)malloc(Imagesize)) == NULL) {
        printf("Failed to apply for black memory...\r\n");
        exit(0);
    }
    /*1.Create a new image cache named IMAGE_RGB and fill it with white*/
    printf("LCD_WIDTH = %d   LCD_HEIGHT  = %d\r\n", LCD_1IN3_WIDTH , LCD_1IN3_HEIGHT);

    Paint_NewImage(BlackImage, LCD_1IN3_WIDTH, LCD_1IN3_HEIGHT, 0, WHITE, 16);
    Paint_Clear(WHITE);
	//Paint_SetRotate(ROTATE_0);
    printf("Listening KEY\r\n");
        /* Press */
    Paint_DrawCircle(90, 120, 25, RED, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
    Paint_DrawString_EN(82, 112, "P", &Font24, IMAGE_BACKGROUND, BLUE);

    /* Left */
    Paint_DrawRectangle(15, 95, 65, 145, RED, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
    Paint_DrawString_EN(32, 112, "L", &Font24, IMAGE_BACKGROUND, BLUE);
// Paint_DrawRectangle( UWORD Color, DOT_PIXEL Line_width, DRAW_FILL Draw_Fill);
    /* Down */
    Paint_DrawRectangle(65, 145, 115, 195, RED, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
    Paint_DrawString_EN(82, 162, "D", &Font24, IMAGE_BACKGROUND, BLUE);

    /* Right */
    Paint_DrawRectangle(115, 95, 165, 145, RED, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
    Paint_DrawString_EN(132, 112, "R", &Font24, IMAGE_BACKGROUND, BLUE);

    /* Up */
    Paint_DrawRectangle(65, 45, 115, 95, RED, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
    Paint_DrawString_EN(82, 62, "U", &Font24, IMAGE_BACKGROUND, BLUE);

    /* Key1 */
    Paint_DrawRectangle(185, 35, 235, 85, RED, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
    Paint_DrawString_EN(195, 52, "K1", &Font24, IMAGE_BACKGROUND, BLUE);
    
    /* Key2	*/
    Paint_DrawRectangle(185, 95, 235, 145, RED, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
    Paint_DrawString_EN(195, 112, "K2", &Font24, IMAGE_BACKGROUND, BLUE);

    /* Key3 */
    Paint_DrawRectangle(185, 155, 235, 205, RED, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
    Paint_DrawString_EN(195, 172, "K3", &Font24, IMAGE_BACKGROUND, BLUE);

    LCD_1IN3_Display(BlackImage);

    for(;;) {
        if(GET_KEY_UP == 0){
            while(GET_KEY_UP == 0){
                Paint_DrawRectangle(65, 45, 115, 95, RED, DOT_PIXEL_1X1, DRAW_FILL_FULL);
                Paint_DrawString_EN(82, 62, "U", &Font24, IMAGE_BACKGROUND, BLUE);
                GUI_Partial_Refresh(65, 45, 115, 95);
            }
            Paint_DrawRectangle(65, 45, 115, 95, WHITE, DOT_PIXEL_1X1, DRAW_FILL_FULL);
            Paint_DrawRectangle(65, 45, 115, 95, RED, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
            Paint_DrawString_EN(82, 62, "U", &Font24, IMAGE_BACKGROUND, BLUE);
            GUI_Partial_Refresh(65, 45, 115, 95);
        }
        if(GET_KEY_DOWN == 0){
            while(GET_KEY_DOWN == 0) {
                Paint_DrawRectangle(65, 145, 115, 195, RED, DOT_PIXEL_1X1, DRAW_FILL_FULL);
                Paint_DrawString_EN(82, 162, "D", &Font24, IMAGE_BACKGROUND, BLUE);
                GUI_Partial_Refresh(65, 145, 115, 195);
            }
            Paint_DrawRectangle(65, 145, 115, 195, WHITE, DOT_PIXEL_1X1, DRAW_FILL_FULL);
            Paint_DrawRectangle(65, 145, 115, 195, RED, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
            Paint_DrawString_EN(82, 162, "D", &Font24, IMAGE_BACKGROUND, BLUE);
            GUI_Partial_Refresh(65, 145, 115, 195);
        }
        
        if(GET_KEY_LEFT == 0) {
            while(GET_KEY_LEFT == 0) {
                Paint_DrawRectangle(15, 95, 65, 145, RED, DOT_PIXEL_1X1, DRAW_FILL_FULL);
                Paint_DrawString_EN(32, 112, "L", &Font24, IMAGE_BACKGROUND, BLUE);
                GUI_Partial_Refresh(15, 95, 65, 145);
            }
            Paint_DrawRectangle(15, 95, 65, 145, WHITE, DOT_PIXEL_1X1, DRAW_FILL_FULL);
            Paint_DrawRectangle(15, 95, 65, 145, RED, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
            Paint_DrawString_EN(32, 112, "L", &Font24, IMAGE_BACKGROUND, BLUE);
            GUI_Partial_Refresh(15, 95, 65, 145);
        }
        if(GET_KEY_RIGHT == 0) {
            while(GET_KEY_RIGHT == 0) {
                Paint_DrawRectangle(115, 95, 165, 145, RED, DOT_PIXEL_1X1, DRAW_FILL_FULL);
                Paint_DrawString_EN(132, 112, "R", &Font24, IMAGE_BACKGROUND, BLUE);
                GUI_Partial_Refresh(115, 95, 165, 145);
            }
            Paint_DrawRectangle(115, 95, 165, 145, WHITE, DOT_PIXEL_1X1, DRAW_FILL_FULL);
            Paint_DrawRectangle(115, 95, 165, 145, RED, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
            Paint_DrawString_EN(132, 112, "R", &Font24, IMAGE_BACKGROUND, BLUE);
            GUI_Partial_Refresh(115, 95, 165, 145);
        }
        if(GET_KEY_PRESS == 0) {
            while(GET_KEY_PRESS == 0) {
                Paint_DrawRectangle(66, 95, 114, 144, RED, DOT_PIXEL_1X1, DRAW_FILL_FULL);
                Paint_DrawString_EN(82, 112, "P", &Font24, IMAGE_BACKGROUND, BLUE);
                GUI_Partial_Refresh(65, 95, 115, 145);
            }
            Paint_DrawRectangle(65, 95, 115, 145, WHITE, DOT_PIXEL_1X1, DRAW_FILL_FULL);
            Paint_DrawCircle(90, 120, 25, RED, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
            Paint_DrawRectangle(65, 95, 115, 145, RED, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
            Paint_DrawString_EN(82, 112, "P", &Font24, IMAGE_BACKGROUND, BLUE);
            GUI_Partial_Refresh(65 , 95, 115, 145);
        }
        if(GET_KEY1 == 0) {
            while(GET_KEY1 == 0) {
                Paint_DrawRectangle(185, 35, 235, 85, RED, DOT_PIXEL_1X1, DRAW_FILL_FULL);
                Paint_DrawString_EN(195, 52, "K1", &Font24, IMAGE_BACKGROUND, BLUE);
                GUI_Partial_Refresh(185, 35, 235, 85);
            }
            Paint_DrawRectangle(184, 35, 235, 85, WHITE, DOT_PIXEL_1X1, DRAW_FILL_FULL);
            Paint_DrawString_EN(195, 52, "K1", &Font24, IMAGE_BACKGROUND, BLUE);
            Paint_DrawRectangle(185, 35, 235, 85, RED, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
            GUI_Partial_Refresh(185, 35, 235, 85);

        }
        if(GET_KEY2 == 0) {
            while(GET_KEY2 == 0) {
                Paint_DrawRectangle(185, 95, 235, 145, RED, DOT_PIXEL_1X1, DRAW_FILL_FULL);
                Paint_DrawString_EN(195, 112, "K2", &Font24, IMAGE_BACKGROUND, BLUE);
                GUI_Partial_Refresh(185, 95, 235, 145);
            }
            Paint_DrawRectangle(185, 95, 235, 145, WHITE, DOT_PIXEL_1X1, DRAW_FILL_FULL);
            Paint_DrawRectangle(185, 95, 235, 145, RED, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
            Paint_DrawString_EN(195, 112, "K2", &Font24, IMAGE_BACKGROUND, BLUE);
            GUI_Partial_Refresh(185, 95, 235, 145);
        }
        if(GET_KEY3 == 0) {
            while(GET_KEY3 == 0) {
                Paint_DrawRectangle(185, 155, 235, 205, RED, DOT_PIXEL_1X1, DRAW_FILL_FULL);
                Paint_DrawString_EN(195, 172, "K3", &Font24, IMAGE_BACKGROUND, BLUE);
                GUI_Partial_Refresh(185, 155, 235, 205);
            }
            Paint_DrawRectangle(185, 155, 235, 205, WHITE, DOT_PIXEL_1X1, DRAW_FILL_FULL);
            Paint_DrawRectangle(185, 155, 235, 205, RED, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
            Paint_DrawString_EN(195, 172, "K3", &Font24, IMAGE_BACKGROUND, BLUE);
            GUI_Partial_Refresh(185, 155, 235, 205);
        }
    }

}