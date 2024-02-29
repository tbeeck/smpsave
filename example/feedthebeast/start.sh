#!/bin/bash

cmd="jre/jdk8u312-b07-jre/bin/java -javaagent:log4jfix/Log4jPatcher-1.0.0.jar -XX:+UseG1GC -XX:+UnlockExperimentalVMOptions -Xmx6144M -Xms4096M -jar forge-1.12.2-14.23.5.2858.jar nogui"
exec $cmd &>/dev/null & disown
