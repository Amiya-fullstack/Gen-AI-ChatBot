for(let i =0;i< 5; i++){
    if(i === 0){
        callFunction();
    }else{
    setTimeout(() => {
        callFunction()
    }, i*1000);
}
}

function callFunction(){
        console.log('helloWorld');
}