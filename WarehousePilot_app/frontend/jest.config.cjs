module.exports = {
  testEnvironment: 'jest-environment-jsdom',
  setupFilesAfterEnv: ['<rootDir>/setupTests.js'],
  moduleNameMapper: {
    '\\.(css|less)$': 'identity-obj-proxy',
    '\\.(svg)$': '<rootDir>/jest-svg-mock.js '
  },
  transform: {
    '^.+\\.(js|jsx)$': 'babel-jest'
  }
};