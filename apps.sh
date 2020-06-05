for app in /usr/share/applications/*.desktop; 
    do 
        echo ${app:24:-8} >> installed_apps_info.txt; 

    done