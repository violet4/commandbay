import Image from "next/image";


const NavbarTop = () => {
    return (
      <div className="w-full flex items-center justify-between h-16 px-4">
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
          <Image src="/commandbay.png" width={40} height={40} alt="Command Bay Logo" />
        </div>
      </div>
    );
  };

export default NavbarTop;
