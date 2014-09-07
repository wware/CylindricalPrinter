/*
 * Arduino code to move the stepper motor.
 */


#include <stdlib.h>

// GPIOs for stepping the steppr
#define DIRECTION 12
#define STEP 13

// microseconds
#define STEPPER_MOTOR_MIN_TIME   500
#define STEPPER_MOTOR_MAX_TIME   1500
#define DELAY_INCREMENT  10
#define THRESHOLD \
    ((STEPPER_MOTOR_MAX_TIME - STEPPER_MOTOR_MIN_TIME) / DELAY_INCREMENT)

char buf[10];
int bufptr;

int moving;
int current_wait;
long begin_stepdown, end_stepup;

void setup() {
    Serial.begin(9600);
    pinMode(STEP, OUTPUT);
    pinMode(DIRECTION, OUTPUT);
    digitalWrite(STEP, LOW);
    digitalWrite(DIRECTION, LOW);
    bufptr = 0;
    moving = 0;
}

void initialize_wait_time(long steps) {
    current_wait = STEPPER_MOTOR_MAX_TIME;
    if (steps >= 2 * THRESHOLD) {
        end_stepup = steps - THRESHOLD;
        begin_stepdown = THRESHOLD;
    }
    else {
        end_stepup = begin_stepdown = steps / 2;
    }
}

void update_wait_time(long steps) {
    if (steps > end_stepup) {
        current_wait -= DELAY_INCREMENT;
    }
    else if (steps < begin_stepdown) {
        current_wait += DELAY_INCREMENT;
    }
}

void one_step() {
    delayMicroseconds(current_wait);
    digitalWrite(STEP, HIGH);
    delayMicroseconds(current_wait);
    digitalWrite(STEP, LOW);
}

void loop() {
    int dir;
    long steps;
    char c;
    if (Serial.available()) {
        c = (char)Serial.read();
        if (!moving) {
            buf[bufptr++] = c;
            switch (c) {
            case '\n':
                buf[--bufptr] == '\0';
                steps = atol(buf);
                if (steps < 0) {
                    digitalWrite(DIRECTION, HIGH);
                    steps = -steps;
                } else {
                    digitalWrite(DIRECTION, LOW);
                }

                initialize_wait_time(steps);
                while (steps > 0) {
                    one_step();
                    steps--;
                    update_wait_time(steps);
                }
                Serial.println("OK");
                bufptr = 0;
                break;
            case 'P':
                digitalWrite(DIRECTION, LOW);
                current_wait = STEPPER_MOTOR_MAX_TIME;
                moving = 1;
                bufptr = 0;
                break;
            case 'N':
                digitalWrite(DIRECTION, HIGH);
                current_wait = STEPPER_MOTOR_MAX_TIME;
                moving = 1;
                bufptr = 0;
                break;
            }
        }
        else if (c == 'S') {
            moving = 2;
        }
    }

    switch (moving) {
      case 0:
        // we're stopped, do nothing
        break;
      case 1:
        one_step();
        // if not at max speed, accelerate
        if (current_wait > STEPPER_MOTOR_MIN_TIME)
            current_wait -= DELAY_INCREMENT;
        break;
      case 2:
        one_step();
        // if not at min speed, decelerate
        if (current_wait < STEPPER_MOTOR_MAX_TIME)
            current_wait += DELAY_INCREMENT;
        else
            // when deceleration complete, stop moving
            moving = 0;
        break;
    }
}
