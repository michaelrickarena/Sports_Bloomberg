"use client";
import classNames from "classnames";

type IButtonProps = {
  xl?: boolean;
  children: string;
};

const Button = (props: IButtonProps) => {
  const btnClass = classNames(
    "inline-block rounded-md text-center text-white bg-primary-500 hover:bg-primary-600 transition-colors duration-200 cursor-pointer",
    {
      "font-extrabold text-xl py-4 px-6": props.xl,
      "text-lg font-semibold py-2 px-4": !props.xl,
    }
  );

  return <div className={btnClass}>{props.children}</div>;
};

export { Button };
