/*
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025 SwatKat1977

This program is free software : you can redistribute it and /or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.If not, see < https://www.gnu.org/licenses/>.
*/
#ifndef WEBWEAVEREXCEPTIONS_H_
#define WEBWEAVEREXCEPTIONS_H_
#include <stdexcept>
#include <string>

namespace WebWeaver { namespace Executor {

class WebWeaverException : public std::runtime_error {
 public:
    using std::runtime_error::runtime_error;
};

class TestSuiteSchemaFileNotFound : public WebWeaverException {
 public:
    using WebWeaverException::WebWeaverException;
};

class TestSuiteSchemaParseFailed : public WebWeaverException {
 public:
     using WebWeaverException::WebWeaverException;
};

class TestSuiteFileNotFound : public WebWeaverException {
 public:
    using WebWeaverException::WebWeaverException;
};

class TestSuiteParseFailed : public WebWeaverException {
 public:
    using WebWeaverException::WebWeaverException;
};

}   // namespace Executor
}   // namespace WebWeaver

#endif  // WEBWEAVEREXCEPTIONS_H_
