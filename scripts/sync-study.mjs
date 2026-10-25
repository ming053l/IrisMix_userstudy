import {cpSync,mkdirSync,rmSync} from 'node:fs';
rmSync('public/study',{recursive:true,force:true});mkdirSync('public/study',{recursive:true});cpSync('work/user_study/site','public/study',{recursive:true});
