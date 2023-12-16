import Image from "next/image";


const NavbarTop = ({height}: {height: number}) => {
    return (
      <div className={`pt-[${height}px] w-full flex items-center justify-between px-4`}>
        {/* Left side - for example, back button or menu toggle */}
        <div className="flex items-center space-x-2">
          {/* Icons/Links */}
        </div>

        <div className="hidden md:flex md:flex-1 md:justify-center">
          {/* Center content here, if desired */}
        </div>

        {/* Right side - for additional actions */}
        <div className="flex items-center space-x-2">
          {/* Icons/Links */}
          <Image src="/commandbay.png" width={height} height={height} alt="Command Bay Logo" />
        </div>
      </div>
    );
  };

export default NavbarTop;
