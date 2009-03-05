var LATIN_MAP={"À":"A","�?":"A","Â":"A","Ã":"A","Ä":"A","Å":"A","Æ":"AE","Ç":"C","È":"E","É":"E","Ê":"E","Ë":"E","Ì":"I","�?":"I","Î":"I","�?":"I","�?":"D","Ñ":"N","Ò":"O","Ó":"O","Ô":"O","Õ":"O","Ö":"O","�?":"O","Ø":"O","Ù":"U","Ú":"U","Û":"U","Ü":"U","Ű":"U","�?":"Y","Þ":"TH","ß":"ss","à":"a","á":"a","â":"a","ã":"a","ä":"a","å":"a","æ":"ae","ç":"c","è":"e","é":"e","ê":"e","ë":"e","ì":"i","�":"i","î":"i","ï":"i","ð":"d","ñ":"n","ò":"o","ó":"o","ô":"o","õ":"o","ö":"o","ő":"o","ø":"o","ù":"u","ú":"u","û":"u","ü":"u","ű":"u","ý":"y","þ":"th","ÿ":"y"};var LATIN_SYMBOLS_MAP={"©":"(c)"};var GREEK_MAP={"α":"a","β":"b","γ":"g","δ":"d","ε":"e","ζ":"z","η":"h","θ":"8","ι":"i","κ":"k","λ":"l","μ":"m","ν":"n","ξ":"3","ο":"o","π":"p","�?":"r","σ":"s","τ":"t","υ":"y","φ":"f","χ":"x","ψ":"ps","ω":"w","ά":"a","�":"e","ί":"i","ό":"o","�?":"y","ή":"h","ώ":"w","ς":"s","ϊ":"i","ΰ":"y","ϋ":"y","�?":"i","Α":"A","Β":"B","Γ":"G","Δ":"D","Ε":"E","Ζ":"Z","Η":"H","Θ":"8","Ι":"I","Κ":"K","Λ":"L","Μ":"M","�?":"N","Ξ":"3","Ο":"O","Π":"P","Ρ":"R","Σ":"S","Τ":"T","Υ":"Y","Φ":"F","Χ":"X","Ψ":"PS","Ω":"W","Ά":"A","Έ":"E","Ί":"I","Ό":"O","Ύ":"Y","Ή":"H","�?":"W","Ϊ":"I","Ϋ":"Y"};var TURKISH_MAP={"ş":"s","Ş":"S","ı":"i","İ":"I","ç":"c","Ç":"C","ü":"u","Ü":"U","ö":"o","Ö":"O","ğ":"g","Ğ":"G"};var RUSSIAN_MAP={"а":"a","б":"b","в":"v","г":"g","д":"d","е":"e","ё":"yo","ж":"zh","з":"z","и":"i","й":"j","к":"k","л":"l","м":"m","н":"n","о":"o","п":"p","р":"r","�?":"s","т":"t","у":"u","ф":"f","х":"h","ц":"c","ч":"ch","ш":"sh","щ":"sh","ъ":"","ы":"y","ь":"","�?":"e","ю":"yu","�?":"ya","�?":"A","Б":"B","В":"V","Г":"G","Д":"D","Е":"E","�?":"Yo","Ж":"Zh","З":"Z","И":"I","Й":"J","К":"K","Л":"L","М":"M","�?":"N","О":"O","П":"P","Р":"R","С":"S","Т":"T","У":"U","Ф":"F","Х":"H","Ц":"C","Ч":"Ch","Ш":"Sh","Щ":"Sh","Ъ":"","Ы":"Y","Ь":"","�":"E","Ю":"Yu","Я":"Ya"};var UKRAINIAN_MAP={"Є":"Ye","І":"I","Ї":"Yi","�?":"G","є":"ye","і":"i","ї":"yi","ґ":"g"};var CZECH_MAP={"�?":"c","�?":"d","ě":"e","ň":"n","ř":"r","š":"s","ť":"t","ů":"u","ž":"z","Č":"C","Ď":"D","Ě":"E","Ň":"N","Ř":"R","Š":"S","Ť":"T","Ů":"U","Ž":"Z"};var POLISH_MAP={"ą":"a","ć":"c","ę":"e","ł":"l","ń":"n","ó":"o","ś":"s","ź":"z","ż":"z","Ą":"A","Ć":"C","Ę":"e","�?":"L","Ń":"N","Ó":"o","Ś":"S","Ź":"Z","Ż":"Z"};var LATVIAN_MAP={"�?":"a","�?":"c","ē":"e","ģ":"g","ī":"i","ķ":"k","ļ":"l","ņ":"n","š":"s","ū":"u","ž":"z","Ā":"A","Č":"C","Ē":"E","Ģ":"G","Ī":"i","Ķ":"k","Ļ":"L","Ņ":"N","Š":"S","Ū":"u","Ž":"Z"};var ALL_DOWNCODE_MAPS=new Array();ALL_DOWNCODE_MAPS[0]=LATIN_MAP;ALL_DOWNCODE_MAPS[1]=LATIN_SYMBOLS_MAP;ALL_DOWNCODE_MAPS[2]=GREEK_MAP;ALL_DOWNCODE_MAPS[3]=TURKISH_MAP;ALL_DOWNCODE_MAPS[4]=RUSSIAN_MAP;ALL_DOWNCODE_MAPS[5]=UKRAINIAN_MAP;ALL_DOWNCODE_MAPS[6]=CZECH_MAP;ALL_DOWNCODE_MAPS[7]=POLISH_MAP;ALL_DOWNCODE_MAPS[8]=LATVIAN_MAP;var Downcoder=new Object();Downcoder.Initialize=function(){if(Downcoder.map){return}Downcoder.map={};Downcoder.chars="";for(var a in ALL_DOWNCODE_MAPS){var b=ALL_DOWNCODE_MAPS[a];for(var d in b){Downcoder.map[d]=b[d];Downcoder.chars+=d}}Downcoder.regex=new RegExp("["+Downcoder.chars+"]|[^"+Downcoder.chars+"]+","g")};downcode=function(b){Downcoder.Initialize();var c="";var e=b.match(Downcoder.regex);if(e){for(var d=0;d<e.length;d++){if(e[d].length==1){var a=Downcoder.map[e[d]];if(a!=null){c+=a;continue}}c+=e[d]}}else{c=b}return c};function URLify(b,a){b=downcode(b);removelist=["a","an","as","at","before","but","by","for","from","is","in","into","like","of","off","on","onto","per","since","than","the","this","that","to","up","via","with"];r=new RegExp("\\b("+removelist.join("|")+")\\b","gi");b=b.replace(r,"");b=b.replace(/[^-\w\s]/g,"");b=b.replace(/^\s+|\s+$/g,"");b=b.replace(/[-\s]+/g,"-");b=b.toLowerCase();return b.substring(0,a)};