import Link from 'next/link';
import React, { useState, ReactNode } from 'react';

interface NodeProps {
    href?: string;
    title: string;
    children?: ReactNode;
    onToggleDropdown?: (isOpen: boolean) => void;
};

const NavNode: React.FC<NodeProps> = ({children, href=null, title, onToggleDropdown}) => {
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const toggleDropdown = () => {
        const newDropdownOpen = !dropdownOpen;
        setDropdownOpen(newDropdownOpen);
        onToggleDropdown && onToggleDropdown(newDropdownOpen);
    };
    return (
        <li className='relative'>
            {href? (
                <Link href={href} className='block px-4 py-2 hover:bg-gray-200'>{title}</Link>
            ) : (
                <button onClick={toggleDropdown} className={`block px-4 py-2 hover:bg-gray-200 w-full text-left ${dropdownOpen&&'text-orange-400'}`}>
                    {title} {children && '>'}
                </button>
            )}
            {children && dropdownOpen && (
                <ul className="absolute left-full top-0 w-48 bg-white shadow-md mt-1">
                    {children}
                </ul>
            )}
        </li>
    );
};

export default function NavbarLeft() {
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const toggleDropdown = (isOpen: boolean) => {
        setIsDropdownOpen(isOpen);
    };
    return (
        <nav className={`bg-gray-100 shadow-lg h-screen overflow-y-auto ${isDropdownOpen ? 'overflow-y-visible' : 'overflow-y-auto'}`}>
            <ul className="flex flex-col">
                <NavNode title="Home"     href="/" />
                <NavNode title="Users"    href="/users" />
                <NavNode title="Rewards"  href="/rewards" />
                <NavNode title="About"    href="/about" />
                <NavNode title="Documentation" onToggleDropdown={toggleDropdown}>
                    {/* <NavNode title="Sphinx" href="/docs/index.html"/> */}
                    <NavNode title="Sphinx" href="/appdocs"/>
                    {/* <NavNode title="API"    href="/api/v0/docs"/> */}
                    <NavNode title="API"    href="/apidocs"/>
                </NavNode>
            </ul>
        </nav>
    );
};
