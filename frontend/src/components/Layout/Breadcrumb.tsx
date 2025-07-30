import React from 'react';
import { Breadcrumb as AntBreadcrumb } from 'antd';
import { Link } from 'react-router-dom';
import { HomeOutlined } from '@ant-design/icons';
import { useAppStore } from '@/store/appStore';

const Breadcrumb: React.FC = () => {
  const { breadcrumb } = useAppStore();

  if (!breadcrumb || breadcrumb.length === 0) {
    return null;
  }

  const items = [
    {
      title: (
        <Link to="/dashboard">
          <HomeOutlined style={{ marginRight: 4 }} />
          首页
        </Link>
      )
    },
    ...breadcrumb.map((item, index) => ({
      title: item.path && index < breadcrumb.length - 1 ? (
        <Link to={item.path}>{item.title}</Link>
      ) : (
        item.title
      )
    }))
  ];

  return (
    <AntBreadcrumb
      items={items}
      style={{
        margin: '16px 0',
        fontSize: 14
      }}
    />
  );
};

export default Breadcrumb;