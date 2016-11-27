#########################################################################
# File Name: main.sh
# Author: 遇见王斌
# mail: wangbin139967@163.com
# Created Time: Tue 28 Oct 2014 05:09:26 AM CST
#########################################################################
#!/bin/bash

#================================#
#            M A I N             #
#================================#

VERSION=1.0.2
TIME="2016-10-21"
TOOL_PATH=$(cd `dirname $0`; pwd)
export TOOL_PATH
cd  ${TOOL_PATH}
MENUPATH=${TOOL_PATH}/sh_menu/Config            # The default menu file path
MENUTYPE=menu                           # Menu file name suffix
MENUFILE=$MENUPATH/TOOL.$MENUTYPE       # The default menu file
MENUCHAR=%                              # The default menu file separator
FUNTION_DIR=sh_menu/Function
FUNTION_DIR_S=${TOOL_PATH}/${FUNTION_DIR}
menu=0 # The first few menu
tree=0 # The default does not display the menu tree
verbose=0 # The default menu tree diagram does not display with the menu information


#{{{Enter
Enter()
{
	echo
	printf "Press the Enter key to continue..."
	read -s Enter
	echo
}
#}}}
#{{{Chkfile
Chkfile()
{
	if [ ! -f $1 ]
	then
        echo -e "\033[41;37mERR-0:\033[0m Menu file $1 Does not exist..."
        exit 1
	fi
}
#}}}
#{{{Chkinput
Chkinput()
{
	if [ "x$2" = "xa" -o "x$2" = "xx" -o "x$2" = "xh" -o "x$2" = "xb" ]
	then
		return 0
	fi

	expr $2 + 0 >/dev/null 2>&1

	if [ $? -ne 0 ]
	then
        return 1
	fi

	if [ $2 -le 0 -o $2 -gt `awk 'END{print NR}' $1` ]
	then
		return 2
	fi
}
#}}}
#{{{Create_file
Create_file()
{
    > ${MENUFILE}
    if [[ ! -d ${FUNTION_DIR} ]]
    then
        echo "${FUNTION_DIR} not exist"
        exit
    else
        # 清理下菜单配置目录
        [[ ! -z ${MENUPATH} ]] && rm -rf ${MENUPATH}/*.menu
    fi
    find ${FUNTION_DIR} -name "*.sh" | while read SH_FILE
    do
        # 17为sh_menu/Function长度
        if [[ -n ${SH_FILE} ]]
        then
            #echo ${SH_FILE:17}
            FILE_PATH=`echo ${SH_FILE:17}`
            FILE_NAME=`basename "${FILE_PATH}"`
            #echo ${FILE_NAME}
            if [[ "w${FILE_NAME}" == "w${FILE_PATH}"  ]]
            then
                # 表示为一级菜单脚本
                #echo "########"
                echo "${FILE_NAME}%${FUNTION_DIR_S}/${FILE_NAME}" >> ${MENUFILE}
                chmod 777 ${FUNTION_DIR_S}/${FILE_NAME}
            else
                # 需要生成二级菜单
                # Function 目录下的目录名作为打开二级菜单的名称
                SUB_MENU_NAME=`echo ${FILE_PATH} | awk -F / '{print $1}'`

                # 将目录名称写到一级菜单中
                echo "${SUB_MENU_NAME}%${SUB_MENU_NAME}.menu" >> ${MENUFILE}

                # 将 Function 二级目录下的脚本写到二级菜单中
                echo "${FILE_NAME}%${FUNTION_DIR_S}/${FILE_PATH}" >> ${MENUPATH}/${SUB_MENU_NAME}.menu
                chmod +x ${FUNTION_DIR_S}/${FILE_PATH}
            fi
        fi
    done
    sh main.sh -t
    echo "OK"
}
#}}}
#{{{Tree
Tree()
{
menu=`expr $menu + 1`
local i=1
until [ $i -gt `awk 'END{print NR}' $1` ]
do

  echo $tree | awk '{for(i=1;i<="'$menu'";i++)if($i==1){printf "| "}else{printf "    "}}'

  if [ $verbose -eq 1 ]
     then
          text=`awk -F"$MENUCHAR" 'NR=="'$i'"{if($2!~/'$MENUTYPE'/){print $1"     "$2}else{print $1}}' $1`
     else
          text=`awk -F"$MENUCHAR" 'NR=="'$i'"{print $1}' $1`
  fi

  if [ $i -eq `awk 'END{print NR}' $1` ]
     then
         echo "|_$text"
         tree=`echo $tree | awk '{for(i=1;i<=NF;i++){if(i==("'$menu'"+1))$i=0}}END{print $0}'`
     else
         echo "|-$text"
         tree=`echo $tree | awk '{for(i=1;i<=NF;i++){if(i==("'$menu'")+1)$i=1}}END{print $0}'`
  fi
  run=`awk -F"$MENUCHAR" 'NR=="'$i'"{print $2}' $1`
  if [ "`echo $run | awk -F"." '{print $NF}'`" = "$MENUTYPE" ]
     then
          tree="$tree 1"
          Tree $MENUPATH/$run
  fi
  i=`expr $i + 1`
done
menu=`expr $menu - 1`
}
#}}}
#{{{Menu
Menu()
{

menu=`expr $menu + 1`

while true

do

if [ "x$input" = "xx" ]
   then
        exit
fi

clear

echo
echo "You can choose followed options:"
echo
echo -e "\033[43;31m---------------------------------\033[0m"
echo
awk -F"$MENUCHAR" 'NF>1{printf "   "NR". ";if($2~/'$MENUTYPE'$/){printf "+ "}else{printf "* "}printf $1"\n\n"}' $1

echo -e "\033[43;31m---------------------------------\033[0m"
echo

if [ $menu -gt 1 ]
   then
       echo "   b Back    "
       echo
fi
echo  "   h Help    "
echo  "   x Exit    "
echo

printf "Input your choice: "
read input
echo

Chkinput $1 "$input"
if [ $? -ne 0 ]
   then
        com=`echo $input | awk '{print $1}'`
        which $com >/dev/null 2>&1
        if [ $? -ne 0 ]
        then
             echo -e "\033[41;37mERR-1:\033[0m Input error, please input again..."
        else
             eval $input
        fi
        Enter
        continue
fi

case "$input" in

      b) if [ $menu -ne 1 ]
            then
                 menu=`expr $menu - 1`
                 return
         fi
         ;;

      #a)
      #   awk -F"$MENUCHAR" 'BEGIN{
      #                     a=0
      #                    }
      #                   {
      #                     if($2!~/'$MENUTYPE'$/){
      #                       print $1":";print "---------------------"
      #                       system($2)
      #                       printf "\n"
      #                       a+=1
      #                       }
      #                    }
      #                END{
      #                     if(a==0)
      #                        print "Non executable statement / scripts, please enter the serial number to open the corresponding sub menu"
      #                   }' $1
      #   Enter
      #   ;;

      h) clear
	     echo -e "\033[42;37m                 Help information                \033[m"
         echo "-------------------------------------------------"
         echo
	     echo -e "\033[42;37m                 version $VERSION                   \033[m"
         echo
         echo "    input number to open a menu/run a script"
         echo
         echo "    [tips] + That is a menu"
         echo "           * That is a script"
         echo
         echo "    b Back"
         echo "    h Help"
         echo "    x Exit" 
         echo
         echo "-------------------------------------------------"
         echo -e "   \033[44;37mAuthor :\033[0m 遇见王斌                             "
         echo -e "   \033[44;37mE-mail :\033[0m wangbin139967@163.com               "
         echo -e "   \033[44;37mTime   :\033[0m ${TIME}                          "
         echo "-------------------------------------------------"
         Enter
         ;;

      x) exit
         ;;

      *) run=`awk -F"$MENUCHAR" 'NR=="'$input'"{print $2}' $1`
         if [ "`echo $run | awk -F"." '{print $NF}'`" = "$MENUTYPE" ]
            then
                 if [ ! -f $MENUPATH/$run ]
                    then
                         echo -e "\033[41;37mERR-0:\033[0m Menu file $MENUPATH/$run Does not exist..."
                         Enter
                    else
                         Menu $MENUPATH/$run
                 fi
            else
                 eval $run
                 Enter
         fi
         ;;
esac

done
 
}
#}}}
while getopts vtcf:h OPTION
do
        case $OPTION in

                t)
                   tree=1
                   ;;
                v)
                   verbose=1
                   echo ${VERSION}
                   exit 0
                   ;;
                f)
                   MENUFILE=$MENUPATH/`echo $OPTARG | sed "s/\.$MENUTYPE$//"`.$MENUTYPE
                   ;;
                c)
                   Create_file
                   exit 0
                   ;;
                h)
                   echo
                   echo "HELP"
                   echo
                   echo "Usage: `basename $0` [-t[-v]] [-c] [-h] [-f file]"
                   echo
                   echo "-t, --Tree"
                   echo
                   echo "-v"
                   echo
                   echo "-c"
                   echo
                   echo "-f file "
                   echo
                   echo "-h, --Help  "
                   echo
                   exit
                   ;;
                *)
                   echo "Please try to execute\"`basename $0` -h\"To get more information."
                   exit 1
                   ;;
        esac
done

if [ $tree -eq 1 ]
   then
        Chkfile $MENUFILE
        tree=0
        echo
        echo "Menu list"
        Tree $MENUFILE
   else
        Chkfile $MENUFILE
        Menu $MENUFILE
fi
