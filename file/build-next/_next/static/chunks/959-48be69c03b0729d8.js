(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[959],{5565:(e,t,n)=>{"use strict";n.d(t,{default:()=>i.a});var r=n(4146),i=n.n(r)},7970:(e,t,n)=>{"use strict";Object.defineProperty(t,"__esModule",{value:!0}),Object.defineProperty(t,"Image",{enumerable:!0,get:function(){return S}});let r=n(306),i=n(9955),s=n(5155),o=i._(n(2115)),u=r._(n(7650)),l=r._(n(6107)),a=n(666),d=n(1159),c=n(3621);n(2363);let f=n(3576),h=r._(n(5514)),p=n(5353),m={deviceSizes:[640,750,828,1080,1200,1920,2048,3840],imageSizes:[16,32,48,64,96,128,256,384],path:"/_next/image/",loader:"default",dangerouslyAllowSVG:!1,unoptimized:!0};function g(e,t,n,r,i,s,o){let u=null==e?void 0:e.src;e&&e["data-loaded-src"]!==u&&(e["data-loaded-src"]=u,("decode"in e?e.decode():Promise.resolve()).catch(()=>{}).then(()=>{if(e.parentElement&&e.isConnected){if("empty"!==t&&i(!0),null==n?void 0:n.current){let t=new Event("load");Object.defineProperty(t,"target",{writable:!1,value:e});let r=!1,i=!1;n.current({...t,nativeEvent:t,currentTarget:e,target:e,isDefaultPrevented:()=>r,isPropagationStopped:()=>i,persist:()=>{},preventDefault:()=>{r=!0,t.preventDefault()},stopPropagation:()=>{i=!0,t.stopPropagation()}})}(null==r?void 0:r.current)&&r.current(e)}}))}function _(e){return o.use?{fetchPriority:e}:{fetchpriority:e}}"undefined"==typeof window&&(globalThis.__NEXT_IMAGE_IMPORTED=!0);let v=(0,o.forwardRef)((e,t)=>{let{src:n,srcSet:r,sizes:i,height:u,width:l,decoding:a,className:d,style:c,fetchPriority:f,placeholder:h,loading:m,unoptimized:v,fill:y,onLoadRef:S,onLoadingCompleteRef:b,setBlurComplete:w,setShowAltText:j,sizesInput:C,onLoad:x,onError:z,...R}=e,O=(0,o.useCallback)(e=>{e&&(z&&(e.src=e.src),e.complete&&g(e,h,S,b,w,v,C))},[n,h,S,b,w,z,v,C]),P=(0,p.useMergedRef)(t,O);return(0,s.jsx)("img",{...R,..._(f),loading:m,width:l,height:u,decoding:a,"data-nimg":y?"fill":"1",className:d,style:c,sizes:i,srcSet:r,src:n,ref:P,onLoad:e=>{g(e.currentTarget,h,S,b,w,v,C)},onError:e=>{j(!0),"empty"!==h&&w(!0),z&&z(e)}})});function y(e){let{isAppRouter:t,imgAttributes:n}=e,r={as:"image",imageSrcSet:n.srcSet,imageSizes:n.sizes,crossOrigin:n.crossOrigin,referrerPolicy:n.referrerPolicy,..._(n.fetchPriority)};return t&&u.default.preload?(u.default.preload(n.src,r),null):(0,s.jsx)(l.default,{children:(0,s.jsx)("link",{rel:"preload",href:n.srcSet?void 0:n.src,...r},"__nimg-"+n.src+n.srcSet+n.sizes)})}let S=(0,o.forwardRef)((e,t)=>{let n=(0,o.useContext)(f.RouterContext),r=(0,o.useContext)(c.ImageConfigContext),i=(0,o.useMemo)(()=>{var e;let t=m||r||d.imageConfigDefault,n=[...t.deviceSizes,...t.imageSizes].sort((e,t)=>e-t),i=t.deviceSizes.sort((e,t)=>e-t),s=null==(e=t.qualities)?void 0:e.sort((e,t)=>e-t);return{...t,allSizes:n,deviceSizes:i,qualities:s}},[r]),{onLoad:u,onLoadingComplete:l}=e,p=(0,o.useRef)(u);(0,o.useEffect)(()=>{p.current=u},[u]);let g=(0,o.useRef)(l);(0,o.useEffect)(()=>{g.current=l},[l]);let[_,S]=(0,o.useState)(!1),[b,w]=(0,o.useState)(!1),{props:j,meta:C}=(0,a.getImgProps)(e,{defaultLoader:h.default,imgConf:i,blurComplete:_,showAltText:b});return(0,s.jsxs)(s.Fragment,{children:[(0,s.jsx)(v,{...j,unoptimized:C.unoptimized,placeholder:C.placeholder,fill:C.fill,onLoadRef:p,onLoadingCompleteRef:g,setBlurComplete:S,setShowAltText:w,sizesInput:e.sizes,ref:t}),C.priority?(0,s.jsx)(y,{isAppRouter:!n,imgAttributes:j}):null]})});("function"==typeof t.default||"object"==typeof t.default&&null!==t.default)&&void 0===t.default.__esModule&&(Object.defineProperty(t.default,"__esModule",{value:!0}),Object.assign(t.default,t),e.exports=t.default)},6562:()=>{},3003:(e,t,n)=>{"use strict";Object.defineProperty(t,"__esModule",{value:!0}),Object.defineProperty(t,"AmpStateContext",{enumerable:!0,get:function(){return r}});let r=n(306)._(n(2115)).default.createContext({})},675:(e,t)=>{"use strict";function n(e){let{ampFirst:t=!1,hybrid:n=!1,hasQuery:r=!1}=void 0===e?{}:e;return t||n&&r}Object.defineProperty(t,"__esModule",{value:!0}),Object.defineProperty(t,"isInAmpMode",{enumerable:!0,get:function(){return n}})},666:(e,t,n)=>{"use strict";Object.defineProperty(t,"__esModule",{value:!0}),Object.defineProperty(t,"getImgProps",{enumerable:!0,get:function(){return u}}),n(2363);let r=n(5859),i=n(1159);function s(e){return void 0!==e.default}function o(e){return void 0===e?e:"number"==typeof e?Number.isFinite(e)?e:NaN:"string"==typeof e&&/^[0-9]+$/.test(e)?parseInt(e,10):NaN}function u(e,t){var n,u;let l,a,d,{src:c,sizes:f,unoptimized:h=!1,priority:p=!1,loading:m,className:g,quality:_,width:v,height:y,fill:S=!1,style:b,overrideSrc:w,onLoad:j,onLoadingComplete:C,placeholder:x="empty",blurDataURL:z,fetchPriority:R,decoding:O="async",layout:P,objectFit:E,objectPosition:F,lazyBoundary:I,lazyRoot:A,...M}=e,{imgConf:k,showAltText:T,blurComplete:N,defaultLoader:D}=t,L=k||i.imageConfigDefault;if("allSizes"in L)l=L;else{let e=[...L.deviceSizes,...L.imageSizes].sort((e,t)=>e-t),t=L.deviceSizes.sort((e,t)=>e-t),r=null==(n=L.qualities)?void 0:n.sort((e,t)=>e-t);l={...L,allSizes:e,deviceSizes:t,qualities:r}}if(void 0===D)throw Error("images.loaderFile detected but the file is missing default export.\nRead more: https://nextjs.org/docs/messages/invalid-images-config");let q=M.loader||D;delete M.loader,delete M.srcSet;let U="__next_img_default"in q;if(U){if("custom"===l.loader)throw Error('Image with src "'+c+'" is missing "loader" prop.\nRead more: https://nextjs.org/docs/messages/next-image-missing-loader')}else{let e=q;q=t=>{let{config:n,...r}=t;return e(r)}}if(P){"fill"===P&&(S=!0);let e={intrinsic:{maxWidth:"100%",height:"auto"},responsive:{width:"100%",height:"auto"}}[P];e&&(b={...b,...e});let t={responsive:"100vw",fill:"100vw"}[P];t&&!f&&(f=t)}let B="",G=o(v),W=o(y);if((u=c)&&"object"==typeof u&&(s(u)||void 0!==u.src)){let e=s(c)?c.default:c;if(!e.src)throw Error("An object should only be passed to the image component src parameter if it comes from a static image import. It must include src. Received "+JSON.stringify(e));if(!e.height||!e.width)throw Error("An object should only be passed to the image component src parameter if it comes from a static image import. It must include height and width. Received "+JSON.stringify(e));if(a=e.blurWidth,d=e.blurHeight,z=z||e.blurDataURL,B=e.src,!S){if(G||W){if(G&&!W){let t=G/e.width;W=Math.round(e.height*t)}else if(!G&&W){let t=W/e.height;G=Math.round(e.width*t)}}else G=e.width,W=e.height}}let H=!p&&("lazy"===m||void 0===m);(!(c="string"==typeof c?c:B)||c.startsWith("data:")||c.startsWith("blob:"))&&(h=!0,H=!1),l.unoptimized&&(h=!0),U&&!l.dangerouslyAllowSVG&&c.split("?",1)[0].endsWith(".svg")&&(h=!0);let V=o(_),$=Object.assign(S?{position:"absolute",height:"100%",width:"100%",left:0,top:0,right:0,bottom:0,objectFit:E,objectPosition:F}:{},T?{}:{color:"transparent"},b),J=N||"empty"===x?null:"blur"===x?'url("data:image/svg+xml;charset=utf-8,'+(0,r.getImageBlurSvg)({widthInt:G,heightInt:W,blurWidth:a,blurHeight:d,blurDataURL:z||"",objectFit:$.objectFit})+'")':'url("'+x+'")',X=J?{backgroundSize:$.objectFit||"cover",backgroundPosition:$.objectPosition||"50% 50%",backgroundRepeat:"no-repeat",backgroundImage:J}:{},Y=function(e){let{config:t,src:n,unoptimized:r,width:i,quality:s,sizes:o,loader:u}=e;if(r)return{src:n,srcSet:void 0,sizes:void 0};let{widths:l,kind:a}=function(e,t,n){let{deviceSizes:r,allSizes:i}=e;if(n){let e=/(^|\s)(1?\d?\d)vw/g,t=[];for(let r;r=e.exec(n);r)t.push(parseInt(r[2]));if(t.length){let e=.01*Math.min(...t);return{widths:i.filter(t=>t>=r[0]*e),kind:"w"}}return{widths:i,kind:"w"}}return"number"!=typeof t?{widths:r,kind:"w"}:{widths:[...new Set([t,2*t].map(e=>i.find(t=>t>=e)||i[i.length-1]))],kind:"x"}}(t,i,o),d=l.length-1;return{sizes:o||"w"!==a?o:"100vw",srcSet:l.map((e,r)=>u({config:t,src:n,quality:s,width:e})+" "+("w"===a?e:r+1)+a).join(", "),src:u({config:t,src:n,quality:s,width:l[d]})}}({config:l,src:c,unoptimized:h,width:G,quality:V,sizes:f,loader:q});return{props:{...M,loading:H?"lazy":m,fetchPriority:R,width:G,height:W,decoding:O,className:g,style:{...$,...X},sizes:Y.sizes,srcSet:Y.srcSet,src:w||Y.src},meta:{unoptimized:h,priority:p,placeholder:x,fill:S}}}},6107:(e,t,n)=>{"use strict";var r=n(2818);Object.defineProperty(t,"__esModule",{value:!0}),function(e,t){for(var n in t)Object.defineProperty(e,n,{enumerable:!0,get:t[n]})}(t,{default:function(){return g},defaultHead:function(){return f}});let i=n(306),s=n(9955),o=n(5155),u=s._(n(2115)),l=i._(n(1172)),a=n(3003),d=n(1147),c=n(675);function f(e){void 0===e&&(e=!1);let t=[(0,o.jsx)("meta",{charSet:"utf-8"},"charset")];return e||t.push((0,o.jsx)("meta",{name:"viewport",content:"width=device-width"},"viewport")),t}function h(e,t){return"string"==typeof t||"number"==typeof t?e:t.type===u.default.Fragment?e.concat(u.default.Children.toArray(t.props.children).reduce((e,t)=>"string"==typeof t||"number"==typeof t?e:e.concat(t),[])):e.concat(t)}n(2363);let p=["name","httpEquiv","charSet","itemProp"];function m(e,t){let{inAmpMode:n}=t;return e.reduce(h,[]).reverse().concat(f(n).reverse()).filter(function(){let e=new Set,t=new Set,n=new Set,r={};return i=>{let s=!0,o=!1;if(i.key&&"number"!=typeof i.key&&i.key.indexOf("$")>0){o=!0;let t=i.key.slice(i.key.indexOf("$")+1);e.has(t)?s=!1:e.add(t)}switch(i.type){case"title":case"base":t.has(i.type)?s=!1:t.add(i.type);break;case"meta":for(let e=0,t=p.length;e<t;e++){let t=p[e];if(i.props.hasOwnProperty(t)){if("charSet"===t)n.has(t)?s=!1:n.add(t);else{let e=i.props[t],n=r[t]||new Set;("name"!==t||!o)&&n.has(e)?s=!1:(n.add(e),r[t]=n)}}}}return s}}()).reverse().map((e,t)=>{let i=e.key||t;if(r.env.__NEXT_OPTIMIZE_FONTS&&!n&&"link"===e.type&&e.props.href&&["https://fonts.googleapis.com/css","https://use.typekit.net/"].some(t=>e.props.href.startsWith(t))){let t={...e.props||{}};return t["data-href"]=t.href,t.href=void 0,t["data-optimized-fonts"]=!0,u.default.cloneElement(e,t)}return u.default.cloneElement(e,{key:i})})}let g=function(e){let{children:t}=e,n=(0,u.useContext)(a.AmpStateContext),r=(0,u.useContext)(d.HeadManagerContext);return(0,o.jsx)(l.default,{reduceComponentsToState:m,headManager:r,inAmpMode:(0,c.isInAmpMode)(n),children:t})};("function"==typeof t.default||"object"==typeof t.default&&null!==t.default)&&void 0===t.default.__esModule&&(Object.defineProperty(t.default,"__esModule",{value:!0}),Object.assign(t.default,t),e.exports=t.default)},5859:(e,t)=>{"use strict";function n(e){let{widthInt:t,heightInt:n,blurWidth:r,blurHeight:i,blurDataURL:s,objectFit:o}=e,u=r?40*r:t,l=i?40*i:n,a=u&&l?"viewBox='0 0 "+u+" "+l+"'":"";return"%3Csvg xmlns='http://www.w3.org/2000/svg' "+a+"%3E%3Cfilter id='b' color-interpolation-filters='sRGB'%3E%3CfeGaussianBlur stdDeviation='20'/%3E%3CfeColorMatrix values='1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 100 -1' result='s'/%3E%3CfeFlood x='0' y='0' width='100%25' height='100%25'/%3E%3CfeComposite operator='out' in='s'/%3E%3CfeComposite in2='SourceGraphic'/%3E%3CfeGaussianBlur stdDeviation='20'/%3E%3C/filter%3E%3Cimage width='100%25' height='100%25' x='0' y='0' preserveAspectRatio='"+(a?"none":"contain"===o?"xMidYMid":"cover"===o?"xMidYMid slice":"none")+"' style='filter: url(%23b);' href='"+s+"'/%3E%3C/svg%3E"}Object.defineProperty(t,"__esModule",{value:!0}),Object.defineProperty(t,"getImageBlurSvg",{enumerable:!0,get:function(){return n}})},3621:(e,t,n)=>{"use strict";Object.defineProperty(t,"__esModule",{value:!0}),Object.defineProperty(t,"ImageConfigContext",{enumerable:!0,get:function(){return s}});let r=n(306)._(n(2115)),i=n(1159),s=r.default.createContext(i.imageConfigDefault)},1159:(e,t)=>{"use strict";Object.defineProperty(t,"__esModule",{value:!0}),function(e,t){for(var n in t)Object.defineProperty(e,n,{enumerable:!0,get:t[n]})}(t,{VALID_LOADERS:function(){return n},imageConfigDefault:function(){return r}});let n=["default","imgix","cloudinary","akamai","custom"],r={deviceSizes:[640,750,828,1080,1200,1920,2048,3840],imageSizes:[16,32,48,64,96,128,256,384],path:"/_next/image",loader:"default",loaderFile:"",domains:[],disableStaticImages:!1,minimumCacheTTL:60,formats:["image/webp"],dangerouslyAllowSVG:!1,contentSecurityPolicy:"script-src 'none'; frame-src 'none'; sandbox;",contentDispositionType:"attachment",localPatterns:void 0,remotePatterns:[],qualities:void 0,unoptimized:!1}},4146:(e,t,n)=>{"use strict";Object.defineProperty(t,"__esModule",{value:!0}),function(e,t){for(var n in t)Object.defineProperty(e,n,{enumerable:!0,get:t[n]})}(t,{default:function(){return l},getImageProps:function(){return u}});let r=n(306),i=n(666),s=n(7970),o=r._(n(5514));function u(e){let{props:t}=(0,i.getImgProps)(e,{defaultLoader:o.default,imgConf:{deviceSizes:[640,750,828,1080,1200,1920,2048,3840],imageSizes:[16,32,48,64,96,128,256,384],path:"/_next/image/",loader:"default",dangerouslyAllowSVG:!1,unoptimized:!0}});for(let[e,n]of Object.entries(t))void 0===n&&delete t[e];return{props:t}}let l=s.Image},5514:(e,t)=>{"use strict";function n(e){var t;let{config:n,src:r,width:i,quality:s}=e,o=s||(null==(t=n.qualities)?void 0:t.reduce((e,t)=>Math.abs(t-75)<Math.abs(e-75)?t:e))||75;return n.path+"?url="+encodeURIComponent(r)+"&w="+i+"&q="+o+(r.startsWith("/_next/static/media/"),"")}Object.defineProperty(t,"__esModule",{value:!0}),Object.defineProperty(t,"default",{enumerable:!0,get:function(){return r}}),n.__next_img_default=!0;let r=n},3576:(e,t,n)=>{"use strict";Object.defineProperty(t,"__esModule",{value:!0}),Object.defineProperty(t,"RouterContext",{enumerable:!0,get:function(){return r}});let r=n(306)._(n(2115)).default.createContext(null)},1172:(e,t,n)=>{"use strict";Object.defineProperty(t,"__esModule",{value:!0}),Object.defineProperty(t,"default",{enumerable:!0,get:function(){return u}});let r=n(2115),i="undefined"==typeof window,s=i?()=>{}:r.useLayoutEffect,o=i?()=>{}:r.useEffect;function u(e){let{headManager:t,reduceComponentsToState:n}=e;function u(){if(t&&t.mountedInstances){let i=r.Children.toArray(Array.from(t.mountedInstances).filter(Boolean));t.updateHead(n(i,e))}}if(i){var l;null==t||null==(l=t.mountedInstances)||l.add(e.children),u()}return s(()=>{var n;return null==t||null==(n=t.mountedInstances)||n.add(e.children),()=>{var n;null==t||null==(n=t.mountedInstances)||n.delete(e.children)}}),s(()=>(t&&(t._pendingUpdate=u),()=>{t&&(t._pendingUpdate=u)})),o(()=>(t&&t._pendingUpdate&&(t._pendingUpdate(),t._pendingUpdate=null),()=>{t&&t._pendingUpdate&&(t._pendingUpdate(),t._pendingUpdate=null)})),null}},5434:(e,t,n)=>{"use strict";var r=n(2818);n(6562);var i=n(2115),s=function(e){return e&&"object"==typeof e&&"default"in e?e:{default:e}}(i),o=void 0!==r&&r.env&&!0,u=function(e){return"[object String]"===Object.prototype.toString.call(e)},l=function(){function e(e){var t=void 0===e?{}:e,n=t.name,r=void 0===n?"stylesheet":n,i=t.optimizeForSpeed,s=void 0===i?o:i;a(u(r),"`name` must be a string"),this._name=r,this._deletedRulePlaceholder="#"+r+"-deleted-rule____{}",a("boolean"==typeof s,"`optimizeForSpeed` must be a boolean"),this._optimizeForSpeed=s,this._serverSheet=void 0,this._tags=[],this._injected=!1,this._rulesCount=0;var l="undefined"!=typeof window&&document.querySelector('meta[property="csp-nonce"]');this._nonce=l?l.getAttribute("content"):null}var t=e.prototype;return t.setOptimizeForSpeed=function(e){a("boolean"==typeof e,"`setOptimizeForSpeed` accepts a boolean"),a(0===this._rulesCount,"optimizeForSpeed cannot be when rules have already been inserted"),this.flush(),this._optimizeForSpeed=e,this.inject()},t.isOptimizeForSpeed=function(){return this._optimizeForSpeed},t.inject=function(){var e=this;if(a(!this._injected,"sheet already injected"),this._injected=!0,"undefined"!=typeof window&&this._optimizeForSpeed){this._tags[0]=this.makeStyleTag(this._name),this._optimizeForSpeed="insertRule"in this.getSheet(),this._optimizeForSpeed||(o||console.warn("StyleSheet: optimizeForSpeed mode not supported falling back to standard mode."),this.flush(),this._injected=!0);return}this._serverSheet={cssRules:[],insertRule:function(t,n){return"number"==typeof n?e._serverSheet.cssRules[n]={cssText:t}:e._serverSheet.cssRules.push({cssText:t}),n},deleteRule:function(t){e._serverSheet.cssRules[t]=null}}},t.getSheetForTag=function(e){if(e.sheet)return e.sheet;for(var t=0;t<document.styleSheets.length;t++)if(document.styleSheets[t].ownerNode===e)return document.styleSheets[t]},t.getSheet=function(){return this.getSheetForTag(this._tags[this._tags.length-1])},t.insertRule=function(e,t){if(a(u(e),"`insertRule` accepts only strings"),"undefined"==typeof window)return"number"!=typeof t&&(t=this._serverSheet.cssRules.length),this._serverSheet.insertRule(e,t),this._rulesCount++;if(this._optimizeForSpeed){var n=this.getSheet();"number"!=typeof t&&(t=n.cssRules.length);try{n.insertRule(e,t)}catch(t){return o||console.warn("StyleSheet: illegal rule: \n\n"+e+"\n\nSee https://stackoverflow.com/q/20007992 for more info"),-1}}else{var r=this._tags[t];this._tags.push(this.makeStyleTag(this._name,e,r))}return this._rulesCount++},t.replaceRule=function(e,t){if(this._optimizeForSpeed||"undefined"==typeof window){var n="undefined"!=typeof window?this.getSheet():this._serverSheet;if(t.trim()||(t=this._deletedRulePlaceholder),!n.cssRules[e])return e;n.deleteRule(e);try{n.insertRule(t,e)}catch(r){o||console.warn("StyleSheet: illegal rule: \n\n"+t+"\n\nSee https://stackoverflow.com/q/20007992 for more info"),n.insertRule(this._deletedRulePlaceholder,e)}}else{var r=this._tags[e];a(r,"old rule at index `"+e+"` not found"),r.textContent=t}return e},t.deleteRule=function(e){if("undefined"==typeof window){this._serverSheet.deleteRule(e);return}if(this._optimizeForSpeed)this.replaceRule(e,"");else{var t=this._tags[e];a(t,"rule at index `"+e+"` not found"),t.parentNode.removeChild(t),this._tags[e]=null}},t.flush=function(){this._injected=!1,this._rulesCount=0,"undefined"!=typeof window?(this._tags.forEach(function(e){return e&&e.parentNode.removeChild(e)}),this._tags=[]):this._serverSheet.cssRules=[]},t.cssRules=function(){var e=this;return"undefined"==typeof window?this._serverSheet.cssRules:this._tags.reduce(function(t,n){return n?t=t.concat(Array.prototype.map.call(e.getSheetForTag(n).cssRules,function(t){return t.cssText===e._deletedRulePlaceholder?null:t})):t.push(null),t},[])},t.makeStyleTag=function(e,t,n){t&&a(u(t),"makeStyleTag accepts only strings as second parameter");var r=document.createElement("style");this._nonce&&r.setAttribute("nonce",this._nonce),r.type="text/css",r.setAttribute("data-"+e,""),t&&r.appendChild(document.createTextNode(t));var i=document.head||document.getElementsByTagName("head")[0];return n?i.insertBefore(r,n):i.appendChild(r),r},function(e,t){for(var n=0;n<t.length;n++){var r=t[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(e,r.key,r)}}(e.prototype,[{key:"length",get:function(){return this._rulesCount}}]),e}();function a(e,t){if(!e)throw Error("StyleSheet: "+t+".")}var d=function(e){for(var t=5381,n=e.length;n;)t=33*t^e.charCodeAt(--n);return t>>>0},c={};function f(e,t){if(!t)return"jsx-"+e;var n=String(t),r=e+n;return c[r]||(c[r]="jsx-"+d(e+"-"+n)),c[r]}function h(e,t){"undefined"==typeof window&&(t=t.replace(/\/style/gi,"\\/style"));var n=e+t;return c[n]||(c[n]=t.replace(/__jsx-style-dynamic-selector/g,e)),c[n]}var p=function(){function e(e){var t=void 0===e?{}:e,n=t.styleSheet,r=void 0===n?null:n,i=t.optimizeForSpeed,s=void 0!==i&&i;this._sheet=r||new l({name:"styled-jsx",optimizeForSpeed:s}),this._sheet.inject(),r&&"boolean"==typeof s&&(this._sheet.setOptimizeForSpeed(s),this._optimizeForSpeed=this._sheet.isOptimizeForSpeed()),this._fromServer=void 0,this._indices={},this._instancesCounts={}}var t=e.prototype;return t.add=function(e){var t=this;void 0===this._optimizeForSpeed&&(this._optimizeForSpeed=Array.isArray(e.children),this._sheet.setOptimizeForSpeed(this._optimizeForSpeed),this._optimizeForSpeed=this._sheet.isOptimizeForSpeed()),"undefined"==typeof window||this._fromServer||(this._fromServer=this.selectFromServer(),this._instancesCounts=Object.keys(this._fromServer).reduce(function(e,t){return e[t]=0,e},{}));var n=this.getIdAndRules(e),r=n.styleId,i=n.rules;if(r in this._instancesCounts){this._instancesCounts[r]+=1;return}var s=i.map(function(e){return t._sheet.insertRule(e)}).filter(function(e){return -1!==e});this._indices[r]=s,this._instancesCounts[r]=1},t.remove=function(e){var t=this,n=this.getIdAndRules(e).styleId;if(function(e,t){if(!e)throw Error("StyleSheetRegistry: "+t+".")}(n in this._instancesCounts,"styleId: `"+n+"` not found"),this._instancesCounts[n]-=1,this._instancesCounts[n]<1){var r=this._fromServer&&this._fromServer[n];r?(r.parentNode.removeChild(r),delete this._fromServer[n]):(this._indices[n].forEach(function(e){return t._sheet.deleteRule(e)}),delete this._indices[n]),delete this._instancesCounts[n]}},t.update=function(e,t){this.add(t),this.remove(e)},t.flush=function(){this._sheet.flush(),this._sheet.inject(),this._fromServer=void 0,this._indices={},this._instancesCounts={}},t.cssRules=function(){var e=this,t=this._fromServer?Object.keys(this._fromServer).map(function(t){return[t,e._fromServer[t]]}):[],n=this._sheet.cssRules();return t.concat(Object.keys(this._indices).map(function(t){return[t,e._indices[t].map(function(e){return n[e].cssText}).join(e._optimizeForSpeed?"":"\n")]}).filter(function(e){return!!e[1]}))},t.styles=function(e){var t,n;return t=this.cssRules(),void 0===(n=e)&&(n={}),t.map(function(e){var t=e[0],r=e[1];return s.default.createElement("style",{id:"__"+t,key:"__"+t,nonce:n.nonce?n.nonce:void 0,dangerouslySetInnerHTML:{__html:r}})})},t.getIdAndRules=function(e){var t=e.children,n=e.dynamic,r=e.id;if(n){var i=f(r,n);return{styleId:i,rules:Array.isArray(t)?t.map(function(e){return h(i,e)}):[h(i,t)]}}return{styleId:f(r),rules:Array.isArray(t)?t:[t]}},t.selectFromServer=function(){return Array.prototype.slice.call(document.querySelectorAll('[id^="__jsx-"]')).reduce(function(e,t){return e[t.id.slice(2)]=t,e},{})},e}(),m=i.createContext(null);m.displayName="StyleSheetContext";var g=s.default.useInsertionEffect||s.default.useLayoutEffect,_="undefined"!=typeof window?new p:void 0;function v(e){var t=_||i.useContext(m);return t&&("undefined"==typeof window?t.add(e):g(function(){return t.add(e),function(){t.remove(e)}},[e.id,String(e.dynamic)])),null}v.dynamic=function(e){return e.map(function(e){return f(e[0],e[1])}).join(" ")},t.style=v},8803:(e,t,n)=>{"use strict";e.exports=n(5434).style}}]);