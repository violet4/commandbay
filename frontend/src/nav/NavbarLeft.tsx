import Link from 'next/link';
import React, { useState, ReactNode } from 'react';

interface NodeProps {
    href?: string;
    title: string;
    children?: ReactNode;
    closeTopNav: () => void;
    setTopDropdown: (isOpen: boolean) => void;
};

//TODO:need side navigation refactor. currently doesn't work as desired, and the code is difficult to work on. the only complexity to see on the screen at a given time should be the logic associated with expanding and collapsing navigation dropdowns. everything else that's simple and already done should be extracted into separate components.
const NavNode: React.FC<NodeProps> = ({children, href=null, title, closeTopNav, setTopDropdown}) => {
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const toggleDropdown = () => {
        const newDropdownOpen = !dropdownOpen;
        setDropdownOpen(newDropdownOpen);
        setTopDropdown(newDropdownOpen);
    };
    return (
        <li className='relative'>
            {href? (
                <Link href={href} className='block px-4 py-2 hover:bg-gray-200' onClick={closeTopNav}>{title}</Link>
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
    const setTopDropdown = (isOpen: boolean) => {
        setIsDropdownOpen(isOpen);
    };
    const closeTopNav = () => setIsDropdownOpen(false);
    return (
        <nav className={`bg-gray-100 shadow-lg h-screen overflow-y-auto ${isDropdownOpen ? 'overflow-y-visible' : 'overflow-y-auto'}`}>
            <ul className="flex flex-col">
                <NavNode title="Home"     href="/" closeTopNav={closeTopNav} setTopDropdown={setTopDropdown} />
                <NavNode title="Users"    href="/users" closeTopNav={closeTopNav} setTopDropdown={setTopDropdown} />
                <NavNode title="Rewards"  href="/rewards" closeTopNav={closeTopNav} setTopDropdown={setTopDropdown} />
                <NavNode title="Settings" href="/settings" closeTopNav={closeTopNav} setTopDropdown={setTopDropdown} />
                <NavNode title="About"    href="/about" closeTopNav={closeTopNav} setTopDropdown={setTopDropdown} />
                <NavNode title="Documentation" href="/appdocs" closeTopNav={closeTopNav} setTopDropdown={setTopDropdown} />
                <NavNode title="API"           href="/apidocs" closeTopNav={closeTopNav} setTopDropdown={setTopDropdown} />
                {/* <NavNode title="Help" closeTopNav={closeTopNav} setTopDropdown={setTopDropdown} >
                </NavNode> */}
            </ul>
        </nav>
    );
};
