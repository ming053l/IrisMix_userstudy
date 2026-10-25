import type {Metadata} from 'next';
import './globals.css';
export const metadata:Metadata={title:'IrisMix User Study',description:'Anonymous bilingual makeup comparison study.'};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="zh-Hant"><body>{children}</body></html>}
