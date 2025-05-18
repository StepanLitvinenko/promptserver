# promptserver

* This is a simple promp client-server application

1. install ollama and run some model
2. patch the server to required model (TODO: configure server, or add into th client request model info)
3. create input json
4. patch th client for send needed json (TODO: convigure client for wotk with command line attr)

* In current version app replace into the promt.txt reg exps: SRC_CODE, TEST_CODE with your input data, descipted in the input.json and send it to server by protocol:
{4_BYTE_LENGTH,TEXT}

where is 4_BYTE_LENGTH it is unsigned int size of the TEXT in bytes



