import Link from 'next/link';
import styles from '@/styles/navbar.module.css'
import React, { useState, ReactNode } from 'react';

interface NodeProps {
    href?: string;
    title: string;
    children?: ReactNode;
};

const NavNode: React.FC<NodeProps> = ({children, href=null, title}) => {
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const toggleDropdown = () => {setDropdownOpen(!dropdownOpen)};
    return (
        <li className='relative'>
            {href? (
                <Link href={href} className='inline-block px-4 py-2'>{title}</Link>
            ) : (
                <button onClick={toggleDropdown} className='inline-block px-4 py-2'>{title}</button>
            )}
            {children && (
                <ul className={`absolute left-0 z-10 mt-2 hidden bg-white`}
                    style={{display: dropdownOpen?'block':'none'}}
                >
                    {children}
                </ul>
            )}
        </li>
    );
};

export default function Navbar() {
    return (
        <nav className="bg-gray-100 shadow-lg">
            <ul className="flex">
                <NavNode title="Home"     href="/" />
                <NavNode title="Users"    href="/users" />
                <NavNode title="Rewards"  href="/rewards" />
                <NavNode title="API Docs" href="/api/v1/docs" />
                <NavNode title="About"    href="/about" />
                <NavNode title="Dropdown">
                    <NavNode title="1"/>
                    <NavNode title="2"/>
                </NavNode>
            </ul>
        </nav>
    );
};

            // <ul>
            //     <li></li>
            //     <li><Link href="/users">Users</Link></li>
            //     <li><Link href="/twitch">Twitch</Link></li>
            //     <li><Link href="/about">About</Link></li>
            //     <li><a href="/api/v1/docs">API Docs</a></li>
            // </ul>
