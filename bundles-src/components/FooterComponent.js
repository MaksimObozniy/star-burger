import React from 'react';

const FooterComponent = () => {
  const style = {
    backgroundColor: "black",
    color: "white",
    padding: "50px 0",
    textAlign: "center"
  };

  return (
    <div style={style}>
      <div className="container">
        <p>© 2026 Star Burger. Контакты: office@star-burger.com</p>
      </div>
    </div>
  );
};

export default FooterComponent;
